# 1 second = 86.5 mel frames
# find max energy position
# expend the width to 3, add tolerance
# detect if it elapse more than 3 frames, if yes, save to memory
# next time, can detect if has such activation
# if recall many times, can explore more features

import librosa, math, time, pyaudio, collections, util, memory, copy, cv2, status
import numpy as np
from scipy import ndimage

start_thread = True
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2  # 16-bit
DEFAULT_PHASE_DURATION = 0.1  # second of buffer

MEL_NUMBER = 128
MFCC_NUMBER = 13

phases = collections.deque()  # phases queue
MAX_PHASES = 5  # max phases storage

db = None
FEATURE = 'ftr'
INDEX = 'nps'
ENERGY = 'ngy'
FEATURE_MAX_ENERGY = 1
FEATURE_MFCC = 2

INPUT_FQC_SIZE = 5
SIMILARITY_THRESHOLD = 0.9
FEATURE_MAP_SIZE = 3
KERNEL = 'kernel'
FEATURE = 'feature'
SIMILAR = 'similar'
FEATURE_DATA = {KERNEL: [], FEATURE: [], SIMILAR: False}
v_filter = {'123': {'filter': [], 'used_count': 0, 'last_used_time': 0, 'memories': {}}}


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
                buffer = stream.read(CHUNK)
                if len(buffer) == 0: break  # reached end of the stream
                np_buffer = np.fromstring(buffer, dtype=np.int16)
                normal_buffer = util.normalizeAudioData(np_buffer)
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


def match(slice_memories):
    distinct_feature_memories = []
    slice_memory_children = {}
    memory.get_live_children(slice_memories, distinct_feature_memories, slice_memory_children)
    for fmm in distinct_feature_memories:
        listen(fmm)
    matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
    return matched_feature_memories


def process(working_memories, work_status, sequential_time_memories):
    slice_memories = [mem for mem in working_memories if mem[memory.MEMORY_DURATION] is memory.SLICE_MEMORY and mem[memory.FEATURE_TYPE] is memory.SOUND]

    matched_feature_memories = match(slice_memories)

    new_feature_memory = hear()
    if len(matched_feature_memories) > 0:
        matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)
    else:
        new_slice_memories = memory.get_live_memories(new_feature_memory, memory.PARENT_MEM)
        new_matched_feature_memories = match(new_slice_memories)
        new_matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(new_matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)


def listen(fmm):
    kernel = fmm[memory.KERNEL]
    feature = fmm[memory.FEATURE]
    fmm.update({memory.STATUS: memory.MATCHING})
    mfcc_map = get_mfcc_map()
    data = filter(mfcc_map, kernel, feature)
    if data[SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory({FEATURE: data[FEATURE]})
        fmm[memory.STATUS] = memory.MATCHED
    return data[SIMILAR]


# match the experience sound sense
def filter(data, kernel, feature=None):
    feature_data = copy.deepcopy(FEATURE_DATA)
    feature_data[KERNEL] = kernel
    cov = cv2.filter2D(data, -1, kernel)
    new_feature = ndimage.maximum_filter(cov, size=FEATURE_MAP_SIZE)
    if feature is None:
        feature_data[FEATURE] = new_feature
    else:
        similarities = abs(new_feature - feature) / feature
        similarity = util.avg(similarities)
        feature_data[SIMILAR] = True
        if similarity > SIMILARITY_THRESHOLD:
            new_feature = (feature + new_feature) / 2
        feature_data[FEATURE] = new_feature
    return feature_data

# get a frequent use kernel or a random kernel by certain possibility
def get_kernel():
    return

def hear():
    kernel = get_kernel()
    data = filter(img, kernel)
    mem = search_memory(kernel, data[FEATURE])
    if mem is None:
        mem = db.add_vision()
    return mem

def get_mfcc_map():
    if len(phases) == 0:
        return None
    mfcc_map = []
    frames = phases.popleft()
    for frame in frames:
        mfcc = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=MFCC_NUMBER)
        mfcc_map.append(mfcc)
    return mfcc_map


# crop a fix size region from source, other value is 0
def crop():
    return
