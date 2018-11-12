# 1 second = 86.5 mel frames
# find max energy position
# expend the width to 3, add tolerance
# detect if it elapse more than 3 frames, if yes, save to memory
# next time, can detect if has such activation
# if recall many times, can explore more features

import librosa, math, time, pyaudio, collections, util, memory, copy, cv2, status, random
import numpy as np
from scipy import ndimage

inited = False
start_thread = True
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2  # 16-bit
DEFAULT_PHASE_DURATION = 0.1  # second of buffer

phases = collections.deque()  # phases queue
MAX_PHASES = 5  # max phases storage
ENERGY_THRESHOLD = 250  # minimum audio energy to consider for processing

db = None

FREQUENCY_WIDTH = 13
ROI_ARR = [3, 5, 9, 13]
ROI_LEVEL = 1
current_range = {}
INPUT_SIZE = 3
SIMILARITY_THRESHOLD = 0.9
VARIANCE_THRESHOLD = 0.3
FEATURE_MAP_SIZE = 3
RANGE_ARR = [3, 5]

KERNEL_FILE = 'uk.npy'
SOUND_KERNEL_FILE = 'vision_kernels90.npy'
used_kernel_rank = None
sound_kernels = None
previous_energies = []

MEMORIES = 'mms'
RANGE = 'rng'

FEATURE_DATA = {memory.KERNEL: [], memory.FEATURE: [], memory.SIMILAR: False}
s_filter = {'123': {'filter': [], 'used_count': 0, 'last_used_time': 0, 'memories': {}}}


def init():
    global inited
    if inited is False:
        global used_kernel_rank
        try:
            used_kernel_rank = np.load(KERNEL_FILE)
        except IOError:
            used_kernel_rank = {}

        global sound_kernels
        sound_kernels = np.load(SOUND_KERNEL_FILE)
        inited = True


def receive(phase_duration=DEFAULT_PHASE_DURATION):
    print 'start to receive data.\n'
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=SAMPLE_RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        while start_thread:
            frame_count = 0
            frame_data = []
            buffer_duration = float(CHUNK) / SAMPLE_RATE
            buffer_count_of_phase = int(math.ceil(phase_duration / buffer_duration))

            # start to record
            while True:
                audio_buffer = stream.read(CHUNK)
                if len(audio_buffer) == 0:
                    break  # reached end of the stream
                np_buffer = np.fromstring(audio_buffer, dtype=np.int16)
                normal_buffer = util.normalize_audio_data(np_buffer)
                frame_data.append(normal_buffer)
                frame_count += 1
                if frame_count >= buffer_count_of_phase:
                    break

            # reach buffer threshold, save it as phase
            if len(phases) > MAX_PHASES:
                # ignore non-process phase
                phases.popleft()
            phases.append(frame_data)

    except KeyboardInterrupt:
        pass


def match(frequency_map, slice_memories):
    distinct_feature_memories = []
    slice_memory_children = {}
    memory.search_sub_memories(slice_memories, distinct_feature_memories, slice_memory_children)
    for fmm in distinct_feature_memories:
        listen(frequency_map, fmm)
    matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
    return matched_feature_memories


def process(working_memories, work_status, sequential_time_memories):
    init()
    frequency_map = get_mfcc_map()
    slice_memories = [mem for mem in working_memories if
                      mem[memory.MEMORY_DURATION] is memory.SLICE_MEMORY and mem[memory.FEATURE_TYPE] is memory.SOUND]

    matched_feature_memories = match(frequency_map, slice_memories)

    new_feature_memory = hear(frequency_map)
    if len(matched_feature_memories) > 0:
        matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)
    else:
        new_slice_memories = memory.get_live_sub_memories(new_feature_memory, memory.PARENT_MEM)
        new_matched_feature_memories = match(frequency_map, new_slice_memories)
        new_matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(new_matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)

    if not work_status[status.BUSY][status.SHORT_DURATION]:
        smm = aware(frequency_map)
        if smm is not None:
            sequential_time_memories[memory.SLICE_MEMORY].append(smm)


def listen(full_frequency_map, fmm):
    kernel = fmm[memory.KERNEL]
    feature = fmm[memory.FEATURE]
    data_range = fmm[RANGE]
    fmm.update({memory.STATUS: memory.MATCHING})
    frequency_map = full_frequency_map[:, data_range[0]:data_range[1]]
    data = filter_feature(frequency_map, kernel, feature)
    if data[memory.SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory(fmm,{memory.FEATURE: data[memory.FEATURE]})
        fmm[memory.STATUS] = memory.MATCHED
    return data[memory.SIMILAR]


# match the experience sound sense
def filter_feature(data, kernel, feature=None):
    fdata = copy.deepcopy(FEATURE_DATA)
    fdata[memory.KERNEL] = kernel
    cov = cv2.filter2D(data, -1, kernel)
    new_feature = ndimage.maximum_filter(cov, size=FEATURE_MAP_SIZE)
    if feature is None:
        fdata[memory.FEATURE] = new_feature
    else:
        similarities = abs(new_feature - feature) / feature
        similarity = util.avg(similarities)
        fdata[memory.SIMILAR] = True
        if similarity > SIMILARITY_THRESHOLD:
            new_feature = (feature + new_feature) / 2
        fdata[memory.FEATURE] = new_feature
    return fdata


# get a frequent use kernel or a random kernel by certain possibility
def get_kernel():
    global used_kernel_rank
    ri = random.randint(0, 9)
    if len(used_kernel_rank) == 0 or ri == 0:
        shape = sound_kernels.shape
        index = random.randint(0, shape[0] - 1)
        return sound_kernels[index]
    else:
        return used_kernel_rank[0]


def get_range():
    index = random.randint(0, len(RANGE_ARR) - 1)
    return RANGE_ARR[index]


# search memory by kernel using index
def search_memory(kernel_id, feature1):
    memory_ids = used_kernel_rank.get(kernel_id)[MEMORIES]
    live_memories = memory.get_live_memories(memory_ids)
    for mem in live_memories:
        feature2 = mem[memory.FEATURE]
        similarity = util.compare_feature(feature1, feature2)
        if similarity > SIMILARITY_THRESHOLD:
            return mem
    return None


def get_range_energy(energy, range_width):
    range_energies = []
    for i in range(0, len(energy) - range_width):
        range_energies.append(np.average(energy[i:i + range_width]))
    return np.array(range_energies)


def expend_max(range_energies, temp_range, range_width):
    new_range = []
    if temp_range[0] > 0:
        if temp_range[1] < len(range_energies):
            left_energy = range_energies[temp_range[0] - 1]
            right_energy = range_energies[temp_range[1] + 1]
            if left_energy >= right_energy:
                new_range.append(temp_range[0] - 1)
                new_range.append(temp_range[1])
            else:
                new_range.append(temp_range[0])
                new_range.append(temp_range[1] + 1)
        else:
            new_range.append(temp_range[0] - 1)
            new_range.append(temp_range[1])
    else:
        new_range.append(temp_range[0])
        new_range.append(temp_range[1] + 1)
    if len(new_range) < range_width:
        expend_max(range_energies, temp_range, range_width)
    else:
        return new_range


# try to find more detail
def hear(full_frequency_map):
    kernel = get_kernel()
    range_width = get_range()
    energies = get_energy(full_frequency_map)
    range_energies = get_range_energy(energies, range_width)
    max_index = np.argmax(range_energies)
    new_range = expend_max(range_energies, [max_index, max_index], range_width)
    frequency_map = full_frequency_map[:, new_range[0]:new_range[1]]
    data = filter_feature(frequency_map, kernel)
    mem = search_memory(kernel, data[memory.FEATURE])
    if mem is None:
        mem = db.add_vision()
    return mem


def get_mfcc_map():
    if len(phases) == 0:
        return None
    mfcc_map = []
    frames = phases.popleft()
    for frame in frames:
        mfcc = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=FREQUENCY_WIDTH)
        mfcc_map.append(mfcc)
    return mfcc_map


def get_energy(frequency_map):
    this_energy = []
    for i in range(0, len(frequency_map)):
        line = frequency_map[i]
        energy = np.average(line)
        this_energy.append(energy)
    return this_energy


def find_most_variable_range(frequency_map):
    range_width = get_range()
    new_range = {}
    this_energies = get_energy(frequency_map)
    global previous_energies
    if len(previous_energies) == 0:
        previous_energies = this_energies
    else:
        previous_range_energies = get_range_energy(previous_energies, range_width)
        this_range_energy = get_range_energy(this_energies, range_width)
        diff_arr = abs(previous_range_energies - this_range_energy) / this_range_energy
        max_index = np.argmax(diff_arr)
        max_var = diff_arr(max_index)
        new_range.update({RANGE: [max_index, max_index + range_width]})
        new_range.update({'v': max_var})
        previous_energies = this_energies
    return new_range


def aware(full_frequency_map):
    range_data = find_most_variable_range(full_frequency_map)
    frequency_map = full_frequency_map[:, range_data[0]:range_data[1]]
    kernel = get_kernel()
    data = filter_feature(frequency_map, kernel)
    if range_data['v'] > VARIANCE_THRESHOLD:
        fmm = memory.add_feature_memory(memory.SOUND, kernel, data[memory.FEATURE])
        smm = memory.add_slice_memory([fmm])
        return smm
    else:
        return None
