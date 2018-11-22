import time, cv2, util, memory, status, copy, random, math
from PIL import ImageGrab, Image
from win32api import GetSystemMetrics
import skimage.measure
import numpy as np

inited = False
db = None

# 1920	960	320	80	16
# 1080	540	180	45	9
screen_width = 0
screen_height = 0
ROI_ARR = [12, 36, 72, 144, 288]
roi_level = 2
current_block = None
START_X = 'sx'
START_Y = 'sy'
WIDTH = 'width'
HEIGHT = 'height'
NUMBER_SUB_REGION = 10
SIMILARITY_THRESHOLD = 0.3
VARIANCE_THRESHOLD = 0.3
FEATURE_INPUT_SIZE = 12
FEATURE_THRESHOLD = 20
POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3

FEATURE_DATA = {memory.KERNEL: [], memory.FEATURE: [], memory.SIMILAR: False}
CHANNEL = 'cnl'

LAST_USED_TIME = 'lut'
MEMORIES = 'mms'
STATUS = 'sts'
IN_PROGRESS = 'pgs'
COMPLETED = 'cmp'
TYPE = 'type'
MOVE = 'move'
DEGREES = 'dgr'
SPEED = 'spd'
DURATION = 'drt'
CREATE_TIME = 'crt'
current_action = {STATUS: COMPLETED, TYPE: MOVE, DEGREES: 0, SPEED: 0, DURATION: 0}
SPEED_FILE = 'us.npy'
DEGREES_FILE = 'ud.npy'
KERNEL_FILE = 'uk.npy'
CHANNEL_FILE = 'uc.npy'
MEMORY_INDEX_FILE = 'mi.npy'
VISION_KERNEL_FILE = 'kernels.npy'
used_speed_rank = None
used_degrees_rank = None
used_kernel_rank = None
used_channel_rank = None
memory_indexes = None
vision_kernels = None
previous_energies = []
previous_block_histogram = []


def init():
    global inited
    if inited is False:
        global screen_width
        screen_width = GetSystemMetrics(0)
        global screen_height
        screen_height = GetSystemMetrics(1)
        global current_block
        center_x = screen_width / 2
        center_y = screen_height / 2
        width = ROI_ARR[roi_level]
        half_width = width / 2
        current_block = {START_X: center_x - half_width, START_Y: center_y - half_width, WIDTH: width, HEIGHT: width}

        # load speed array, degrees
        global used_speed_rank
        try:
            used_speed_rank = np.load(SPEED_FILE)
        except IOError:
            used_speed_rank = np.array([])

        global used_degrees_rank
        try:
            used_degrees_rank = np.load(DEGREES_FILE)
        except IOError:
            used_degrees_rank = np.array([])

        global used_kernel_rank
        try:
            used_kernel_rank = np.load(KERNEL_FILE)
        except IOError:
            used_kernel_rank = np.array([])

        global used_channel_rank
        try:
            used_channel_rank = np.load(CHANNEL_FILE)
        except IOError:
            used_channel_rank = np.array([])

        global memory_indexes
        try:
            memory_indexes = np.load(MEMORY_INDEX_FILE)
        except IOError:
            memory_indexes = np.array([])

        global vision_kernels
        vision_kernels = np.load(VISION_KERNEL_FILE)
        inited = True


def match(slice_memories):
    distinct_feature_memories = []
    slice_memory_children = {}
    memory.search_sub_memories(slice_memories, distinct_feature_memories, slice_memory_children)
    for fmm in distinct_feature_memories:
        watch(fmm)
    matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
    return matched_feature_memories


def save_used_ranks():
    np.save(SPEED_FILE, used_speed_rank)
    global used_degrees_rank
    np.save(DEGREES_FILE, used_degrees_rank)
    global used_kernel_rank
    np.save(KERNEL_FILE, used_kernel_rank)
    global used_channel_rank
    np.save(CHANNEL_FILE, used_channel_rank)


def process(working_memories, work_status, sequential_time_memories):
    init()
    if current_action[STATUS] is IN_PROGRESS:
        calculate_action(current_action)

    slice_memories = [mem for mem in working_memories if
                      mem[memory.MEMORY_DURATION] is memory.SLICE_MEMORY and mem[memory.FEATURE_TYPE] is memory.VISION]

    matched_feature_memories = match(slice_memories)

    new_feature_memory = look()
    if len(matched_feature_memories) > 0:
        if new_feature_memory is not None:
            matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)
    elif new_feature_memory is not None:
        new_slice_memories = memory.get_live_sub_memories(new_feature_memory, memory.PARENT_MEM)
        new_matched_feature_memories = match(new_slice_memories)
        new_matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(new_matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)

    if not work_status[status.BUSY][status.SHORT_DURATION]:
        if current_action[STATUS] is not IN_PROGRESS:
            aware()

    if not work_status[status.BUSY][status.MEDIUM_DURATION] or not work_status[status.REWARD]:
        if current_action[STATUS] is not IN_PROGRESS:
            new_slice_memory = explore()
            sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)

    if not work_status[status.BUSY][status.LONG_DURATION]:
        save_used_ranks()


def watch(fmm):
    channel = fmm[memory.CHANNEL]
    kernel = fmm[memory.KERNEL]
    feature = fmm[memory.FEATURE]
    fmm.update({memory.STATUS: memory.MATCHING})
    img = get_region()
    channel_img = get_channel_region(img, channel)
    data = filter_feature(channel_img, kernel, feature)
    if data is None:
        return False  # not similar
    if data[memory.SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory(fmm, {memory.FEATURE: data[memory.FEATURE]})
        fmm[memory.STATUS] = memory.MATCHED
        update_channel_rank(channel)
        update_kernel_rank(kernel)
    return data[memory.SIMILAR]


# match the experience vision sense
def filter_feature(data, kernel, feature=None):
    feature_data = copy.deepcopy(FEATURE_DATA)
    feature_data[memory.KERNEL] = kernel
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
        feature_data[memory.FEATURE] = new_feature
    else:
        difference = util.compare_feature(new_feature, feature)
        if difference < SIMILARITY_THRESHOLD:
            feature_data[memory.SIMILAR] = True
            avg_feature = (feature + new_feature) / 2
            feature_data[memory.FEATURE] = avg_feature
        else:
            feature_data[memory.FEATURE] = new_feature
    return feature_data


def update_kernel_rank(kernel):
    global used_kernel_rank
    used_kernel_rank = util.update_rank_list(memory.KERNEL, kernel, used_kernel_rank)


# get a frequent use kernel or a random kernel by certain possibility
def get_kernel():
    kernel = util.get_top_rank(used_kernel_rank)
    if kernel is None:
        shape = vision_kernels.shape
        index = random.randint(0, shape[0] - 1)
        kernel = vision_kernels[index]
    return kernel


def update_degrees_rank(degrees):
    global used_degrees_rank
    used_degrees_rank = util.update_rank_list(DEGREES, degrees, used_degrees_rank)


def get_degrees():
    degrees = util.get_top_rank(used_degrees_rank)
    if degrees is None:
        degrees = random.randint(1, 36)
    return degrees


def update_speed_rank(speed):
    global used_speed_rank
    used_speed_rank = util.update_rank_list(SPEED, speed, used_speed_rank)


def get_speed():
    speed = util.get_top_rank(used_speed_rank)
    if speed is None:
        speed = random.randint(1, 40)
    return speed


def update_channel_rank(channel):
    global used_channel_rank
    used_channel_rank = util.update_rank_list(CHANNEL, channel, used_channel_rank)


def get_channel():
    channel = util.get_top_rank(used_channel_rank)
    if channel is None:
        ri = random.randint(1, 3)
        channel = 'y'
        if ri == 1:
            channel = 'u'
        elif ri == 2:
            channel = 'v'
    return channel


def get_duration():
    return random.randint(1, 5) / 10.0


# try to find more detail
def look():
    channel = get_channel()
    img = get_region()
    kernel = get_kernel()
    channel_img = get_channel_region(img, channel)
    data = filter_feature(channel_img, kernel)
    if data is None:
        return None
    mem = search_memory(channel, kernel, data[memory.FEATURE])
    if mem is None:
        mem = memory.add_vision_memory(memory.VISION, channel, kernel, data[memory.FEATURE])
        update_memory_indexes(channel, kernel, mem[memory.ID])
    update_kernel_rank(kernel)
    update_channel_rank(channel)
    return mem


def update_memory_indexes(channel, kernel, mid):
    global memory_indexes
    element = next((x for x in memory_indexes if x[memory.KERNEL] == kernel and x[memory.CHANNEL] == channel), None)
    if element is None:
        new_kernel = {CHANNEL: channel, memory.KERNEL: kernel, MEMORIES: [mid]}
        memory_indexes = np.append(memory_indexes, new_kernel)
    else:
        memory_ids = element[MEMORIES]
        if mid not in memory_ids:
            memory_ids.append(mid)


# search memory by kernel using index
def search_memory(channel, kernel, feature1):
    global memory_indexes
    element = next((x for x in memory_indexes if x[memory.KERNEL] == kernel and x[memory.CHANNEL] == channel), None)
    if element is not None:
        memory_ids = element[MEMORIES]
        live_memories = memory.get_live_memories(memory_ids)
        if live_memories is not None:
            for mem in live_memories:
                feature2 = mem[memory.FEATURE]
                difference = util.compare_feature(feature1, feature2)
                if difference < SIMILARITY_THRESHOLD:
                    return mem
    return None


def calculate_start_x(new_start_x):
    actual_start_x = new_start_x
    if new_start_x < 0:
        actual_start_x = 0
    if new_start_x + current_block[WIDTH] > screen_width:
        actual_start_x = screen_width - current_block[WIDTH]
    return int(round(actual_start_x))


def calculate_start_y(new_start_y):
    actual_start_y = new_start_y
    if new_start_y < 0:
        actual_start_y = 0
    if new_start_y + current_block[HEIGHT] > screen_height:
        actual_start_y = screen_height - current_block[HEIGHT]
    return int(round(actual_start_y))


def calculate_degrees(new_block):
    radians = math.atan2(new_block[START_Y] - current_block[START_Y], new_block[START_X] - current_block[START_X])
    degrees = math.degrees(radians)
    return degrees


def calculate_action(action):
    elapse = time.time() - action[CREATE_TIME]
    new_start_y = current_block[START_Y] + (math.sin(math.radians(action[DEGREES])) * elapse * action[SPEED])
    new_start_x = current_block[START_X] + (math.cos(math.radians(action[DEGREES])) * elapse * action[SPEED])
    current_block[START_X] = calculate_start_x(new_start_x)
    current_block[START_Y] = calculate_start_y(new_start_y)
    if time.time() > (action[CREATE_TIME] + action[DURATION]):
        action.update({STATUS: COMPLETED})


def find_most_variable_region(full_img):
    new_block = {}
    this_block_histogram = []
    width = screen_width / NUMBER_SUB_REGION
    height = screen_height / NUMBER_SUB_REGION
    for i in range(0, NUMBER_SUB_REGION - 1):
        for j in range(0, NUMBER_SUB_REGION - 1):
            ret = full_img[j * height:(j + 1) * height, i * width:(i + 1) * width]
            hist_np, bins = np.histogram(ret.ravel(), 64, [0, 256])
            this_block_histogram.append(hist_np)
    global previous_block_histogram
    if len(previous_block_histogram) == 0:
        previous_block_histogram = this_block_histogram
    else:
        diff_arr = util.histogram_array_diff(this_block_histogram, previous_block_histogram)
        previous_block_histogram = this_block_histogram
        max_index = np.argmax(diff_arr)
        max_var = diff_arr(max_index)
        new_start_x = max_index % NUMBER_SUB_REGION * width
        new_start_y = max_index / NUMBER_SUB_REGION * height
        new_block[START_X] = calculate_start_x(new_start_x)
        new_block[START_Y] = calculate_start_y(new_start_y)
        new_block.update({'v': max_var})
        previous_block_histogram = this_block_histogram
    return new_block


def aware():
    duration = get_duration()
    full_img = ImageGrab.grab()
    block = find_most_variable_region(full_img)
    if block['v'] > VARIANCE_THRESHOLD:
        # move focus to variable region
        set_movement_absolute(block, duration)


def set_movement_absolute(new_block, duration):
    degrees = calculate_degrees(new_block)
    length = math.hypot(new_block[START_Y] - current_block[START_Y], new_block[START_X] - current_block[START_X])
    speed = length / duration
    set_movement_relative(degrees, speed, duration)


def set_movement_relative(degrees, speed, duration):
    global current_action
    current_action = {DEGREES: degrees, SPEED: speed, DURATION: duration, CREATE_TIME: time.time(),
                      memory.ACTOR: memory.VISION}
    action_memory = memory.add_action_memory(current_action)
    slice_memory = memory.add_slice_memory([action_memory[memory.ID]])
    return slice_memory


def explore():
    # random move, explore the world
    degrees = get_degrees()
    update_degrees_rank(degrees)
    # most frequent speed
    speed = get_speed()
    update_speed_rank(speed)
    # 0.1-0.5s
    duration = get_duration()
    slice_memory = set_movement_relative(degrees, speed, duration)
    return slice_memory


def get_channel_region(bgr, channel):
    yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
    y, u, v = cv2.split(yuv)
    if channel is 'y':
        return y
    elif channel is 'u':
        return u
    elif channel is 'v':
        return v


def get_region():
    global current_block
    roi_image = crop(current_block)
    cv_img = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2BGR)
    img = cv2.resize(cv_img, (FEATURE_INPUT_SIZE, FEATURE_INPUT_SIZE))
    return img


def crop(block):
    img = ImageGrab.grab(
        bbox=(block[START_X], block[START_Y], block[START_X] + block[WIDTH], block[START_Y] + block[HEIGHT]))
    return img
