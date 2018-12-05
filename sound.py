import librosa, math, pyaudio, collections, util, memory, copy, cv2, status, random, constants, time
import numpy as np
import skimage.measure

inited = False
start_thread = True
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2  # 16-bit
DEFAULT_PHASE_DURATION = 0.2  # second of buffer
MAX_FREQUENCY = 8000

phases = collections.deque()  # phases queue
MAX_PHASES = 5  # max phases storage
ENERGY_THRESHOLD = 250  # minimum audio energy to consider for processing

FREQUENCY_MAP_HEIGHT = 20
HOP_LENGTH = 512
FEATURE_INPUT_SIZE = 12
FEATURE_THRESHOLD = 10
FEATURE_SIMILARITY_THRESHOLD = 0.2
POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
USED_KERNEL_FILE = 'suk.npy'
MEMORY_INDEX_FILE = 'smi.npy'
SOUND_KERNEL_FILE = 'kernels.npy'
used_kernel_rank = None
sound_kernels = None
memory_indexes = None
previous_phase = None
previous_energies = []

ROI_ARR = [3, 5, 9, 13]
ROI_LEVEL = 1
current_range = {}
RANGE_ARR = [5, 10, 15]
RANGE = 'rng'
REGION_VARIANCE_THRESHOLD = 0.05

FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}
db = None


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
                frame_data = frame_data + normal_buffer.tolist()
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


def init():
    global inited
    if inited is False:
        global memory_indexes
        try:
            memory_indexes = np.load(MEMORY_INDEX_FILE)
        except IOError:
            memory_indexes = np.array([])

        global used_kernel_rank
        try:
            used_kernel_rank = np.load(USED_KERNEL_FILE)
        except IOError:
            used_kernel_rank = np.array([])

        global sound_kernels
        sound_kernels = np.load(SOUND_KERNEL_FILE)
        inited = True


def save_files():
    global memory_indexes
    np.save(MEMORY_INDEX_FILE, memory_indexes)
    global used_kernel_rank
    np.save(USED_KERNEL_FILE, used_kernel_rank)


def process(working_memories, work_status, sequential_time_memories):
    start = time.time()
    init()
    frequency_map = get_frequency_map()
    if frequency_map is None:
        return
    slice_feature_memories = [mem for mem in working_memories if
                              mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and mem[
                                  constants.PHYSICAL_MEMORY_TYPE] is constants.SOUND_FEATURE]

    matched_feature_memories = match_features(frequency_map, slice_feature_memories)

    new_feature_memory = search_feature(frequency_map)
    if len(matched_feature_memories) > 0:
        if new_feature_memory is not None:
            matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(matched_feature_memories)
        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
    elif new_feature_memory is not None:
        new_slice_memories = memory.get_live_sub_memories(new_feature_memory, constants.PARENT_MEM)
        new_matched_feature_memories = match_features(frequency_map, new_slice_memories)
        new_matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(new_matched_feature_memories)
        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)

    # if not work_status[constants.BUSY][constants.SHORT_DURATION]:
    #     smm = aware(frequency_map)
    #     if smm is not None:
    #         sequential_time_memories[constants.SLICE_MEMORY].append(smm)

    if not work_status[constants.BUSY][constants.LONG_DURATION]:
        save_files()
    # print 'process	' + str(time.time() - start)


def match_features(frequency_map, slice_memories):
    distinct_feature_memories = []
    slice_memory_children = {}
    memory.search_sub_memories(slice_memories, distinct_feature_memories, slice_memory_children)
    for fmm in distinct_feature_memories:
        match_feature(frequency_map, fmm)
    matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
    return matched_feature_memories


def match_feature(full_frequency_map, fmm):
    kernel = fmm[constants.KERNEL]
    feature = fmm[constants.FEATURE]
    # data_range = fmm[RANGE]
    # frequency_map = full_frequency_map[data_range[0]:data_range[1], :]
    # data = filter_feature(frequency_map, kernel, feature)
    fmm.update({constants.STATUS: constants.MATCHING})
    data = filter_feature(full_frequency_map, kernel, feature)
    if data is None:
        return False  # not similar
    if data[constants.SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory(fmm, {constants.FEATURE: data[constants.FEATURE]})
        fmm[constants.STATUS] = constants.MATCHED
        update_kernel_rank(kernel)
    return data[constants.SIMILAR]


# match the experience sound sense
def filter_feature(raw, kernel, feature=None):
    # map to image color range
    color_data = raw / (MAX_FREQUENCY / 256)
    data = color_data.astype(np.uint8)
    feature_data = copy.deepcopy(FEATURE_DATA)
    feature_data[constants.KERNEL] = kernel
    data_map = cv2.resize(data, (FEATURE_INPUT_SIZE, FEATURE_INPUT_SIZE))
    kernel_arr = util.string_to_feature_matrix(kernel)
    cov = cv2.filter2D(data_map, -1, kernel_arr)
    # down-sampling once use max pool, size is 50% of origin
    new_feature_pool1 = skimage.measure.block_reduce(cov, (POOL_BLOCK_SIZE, POOL_BLOCK_SIZE), np.max)
    # down-sampling again use max pool, size is 25% of origin
    new_feature_pool2 = skimage.measure.block_reduce(new_feature_pool1, (POOL_BLOCK_SIZE, POOL_BLOCK_SIZE), np.max)
    # reduce not obvious feature
    threshold_feature = np.where(new_feature_pool2 < FEATURE_THRESHOLD, 0, new_feature_pool2)
    if threshold_feature.sum() == 0:
        return None  # no any feature found
    standard_feature = util.standardize_feature(threshold_feature)
    new_feature = standard_feature.flatten().astype(int)
    if feature is None:
        feature_data[constants.FEATURE] = new_feature
    else:
        difference = util.np_array_diff(new_feature, feature)
        if difference < FEATURE_SIMILARITY_THRESHOLD:
            feature_data[constants.SIMILAR] = True
            avg_feature = (feature + new_feature) / 2
            feature_data[constants.FEATURE] = avg_feature
        else:
            feature_data[constants.FEATURE] = new_feature
    return feature_data


# get a frequent use kernel or a random kernel by certain possibility
def get_kernel():
    used_kernel = util.get_high_rank(used_kernel_rank)
    if used_kernel is None:
        shape = sound_kernels.shape
        index = random.randint(0, shape[0] - 1)
        kernel = sound_kernels[index]
        return kernel
    else:
        return used_kernel[constants.KERNEL]


def update_kernel_rank(kernel):
    global used_kernel_rank
    used_kernel_rank = util.update_rank_list(constants.KERNEL, kernel, used_kernel_rank)


# try to find more detail
def search_feature(full_frequency_map):
    kernel = get_kernel()
    # range_width = get_range()
    # energies = get_energy(full_frequency_map)
    # range_energies = get_range_energy(energies, range_width)
    # max_index = np.argmax(range_energies)
    # new_range = expend_max(range_energies, [max_index, max_index], range_width)
    # frequency_map = full_frequency_map[new_range[0]:new_range[1], :]
    # data = filter_feature(frequency_map, kernel)
    data = filter_feature(full_frequency_map, kernel)
    if data is None:
        return None
    mem = search_memory(kernel, data[constants.FEATURE])
    if mem is None:
        mem = memory.add_feature_memory(constants.VISION_FEATURE, kernel, data[constants.FEATURE].tolist())
        update_memory_indexes(kernel, mem[constants.MID])
    update_kernel_rank(kernel)
    return mem


# search memory by kernel using index
def search_memory(kernel, feature1):
    global memory_indexes
    element = next((x for x in memory_indexes if x[constants.KERNEL] == kernel), None)
    if element is not None:
        memory_ids = element[constants.MEMORIES]
        live_memories = memory.get_live_memories(memory_ids)
        if live_memories is not None:
            for mem in live_memories:
                feature2 = mem[constants.FEATURE]
                difference = util.np_array_diff(feature1, feature2)
                if difference < FEATURE_SIMILARITY_THRESHOLD:
                    return mem
    return None


def update_memory_indexes(kernel, mid):
    global memory_indexes
    element = next((x for x in memory_indexes if x[constants.KERNEL] == kernel), None)
    if element is None:
        new_kernel = {constants.KERNEL: kernel, constants.MEMORIES: [mid]}
        memory_indexes = np.append(memory_indexes, new_kernel)
    else:
        memory_ids = element[constants.MEMORIES]
        if mid not in memory_ids:
            memory_ids.append(mid)


def aware(full_frequency_map):
    range_data = find_most_variable_region(full_frequency_map)
    frequency_map = full_frequency_map[range_data[0]:range_data[1], :]
    kernel = get_kernel()
    data = filter_feature(frequency_map, kernel)
    if range_data['v'] > REGION_VARIANCE_THRESHOLD:
        fmm = memory.add_feature_memory(constants.SOUND_FEATURE, kernel, data[constants.FEATURE])
        smm = memory.add_slice_memory([fmm])
        return smm
    else:
        return None


def find_most_variable_region(frequency_map):
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


def get_frequency_map():
    global previous_phase
    if len(phases) == 0:
        return None
    phase = phases.popleft()
    if previous_phase is None:
        previous_phase = phase
        return
    data = np.append(previous_phase, phase)
    map_width = (len(data) / HOP_LENGTH) + 1
    if map_width >= FEATURE_INPUT_SIZE:
        map_height = map_width
    else:
        map_height = FREQUENCY_MAP_HEIGHT
    # frequency_map = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=FREQUENCY_MAP_HEIGHT)
    frequency_map = librosa.feature.melspectrogram(y=data, sr=SAMPLE_RATE, n_mels=map_height, hop_length=HOP_LENGTH,
                                                   fmax=MAX_FREQUENCY)
    previous_phase = phase
    return frequency_map


def get_energy(frequency_map):
    this_energy = []
    for i in range(0, len(frequency_map)):
        line = frequency_map[i]
        energy = np.average(line)
        this_energy.append(energy)
    return this_energy


def get_range():
    index = random.randint(0, len(RANGE_ARR) - 1)
    return RANGE_ARR[index]


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
