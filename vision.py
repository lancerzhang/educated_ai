import time, cv2, util, copy, random, math, memory, constants
from PIL import ImageGrab, Image
# from win32api import GetSystemMetrics
import skimage.measure
import numpy as np

inited = False

# 1920	960	320	80	16
# 1080	540	180	45	9
screen_width = 0
screen_height = 0
ROI_ARR = [12, 36, 72, 144, 288]
roi_index = 2
current_block = None
START_X = 'sx'
START_Y = 'sy'
WIDTH = 'width'
HEIGHT = 'height'
NUMBER_SUB_REGION = 10
FEATURE_SIMILARITY_THRESHOLD = 0.3
IMAGE_VARIANCE_THRESHOLD = 0.05
FEATURE_INPUT_SIZE = 12
FEATURE_THRESHOLD = 20
POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3

FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}
LAST_USED_TIME = 'lut'
MEMORIES = 'mms'
STATUS = 'sts'
IN_PROGRESS = 'pgs'
COMPLETED = 'cmp'
MOVE = 'move'
ZOOM_IN = 'zmi'
ZOOM_OUT = 'zmo'
CREATE_TIME = 'crt'
current_action = {STATUS: COMPLETED}
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

db = None


def init():
    global inited
    if inited is False:
        global screen_width
        # screen_width = GetSystemMetrics(0)
        global screen_height
        # screen_height = GetSystemMetrics(1)
        global current_block
        center_x = screen_width / 2
        center_y = screen_height / 2
        width = ROI_ARR[roi_index]
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


def match_feature(slice_memories):
    distinct_feature_memories = []
    slice_memory_children = {}
    memory.search_sub_memories(slice_memories, distinct_feature_memories, slice_memory_children)
    for fmm in distinct_feature_memories:
        watch(fmm)
    matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
    return matched_feature_memories


def save_used_ranks():
    global used_speed_rank
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

    slice_feature_memories = [mem for mem in working_memories if
                              mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and mem[
                                  constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FEATURE]

    matched_feature_memories = match_feature(slice_feature_memories)

    new_feature_memory = look()
    if len(matched_feature_memories) > 0:
        if new_feature_memory is not None:
            matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(matched_feature_memories)
        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
    elif new_feature_memory is not None:
        new_slice_memories = memory.get_live_sub_memories(new_feature_memory, constants.PARENT_MEM)
        new_matched_feature_memories = match_feature(new_slice_memories)
        new_matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(new_matched_feature_memories)
        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)

    if not work_status[constants.BUSY][constants.SHORT_DURATION]:
        if current_action[STATUS] is not IN_PROGRESS:
            aware()

    if not work_status[constants.BUSY][constants.MEDIUM_DURATION] or not work_status[constants.REWARD]:
        if current_action[STATUS] is not IN_PROGRESS:
            new_slice_memory = explore()
            if new_slice_memory is not None:
                sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)

    if not work_status[constants.BUSY][constants.LONG_DURATION]:
        save_used_ranks()

    slice_movement_memories = [mem for mem in working_memories if
                               mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and mem[
                                   constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FOCUS_MOVE]
    if current_action[STATUS] is not IN_PROGRESS:
        if len(slice_movement_memories) > 0:
            match_movement_memories(slice_movement_memories)

    slice_zoom_memories = [mem for mem in working_memories if
                           mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and mem[
                               constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FOCUS_ZOOM]
    if len(slice_zoom_memories) > 0:
        match_zoom_memories(slice_zoom_memories)


def match_movement_memories(memories):
    mem = memories[0]
    global current_action
    current_action = {constants.DEGREES: mem[constants.DEGREES], constants.SPEED: mem[constants.SPEED],
                      constants.DURATION: mem[constants.DURATION], CREATE_TIME: time.time(),
                      constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE, STATUS: COMPLETED}
    mem[constants.STATUS] = constants.MATCHED
    memory.recall_memory(mem)


def match_zoom_memories(memories):
    mem = memories[0]
    zoom_type = mem[constants.ZOOM_TYPE]
    if zoom_type is ZOOM_OUT:
        zoom_out()
    elif zoom_type is ZOOM_IN:
        zoom_in()
    mem[constants.STATUS] = constants.MATCHED
    memory.recall_memory(mem)


def watch(fmm):
    channel = fmm[constants.CHANNEL]
    kernel = fmm[constants.KERNEL]
    feature = fmm[constants.FEATURE]
    fmm.update({constants.STATUS: constants.MATCHING})
    img = get_region()
    channel_img = get_channel_region(img, channel)
    data = filter_feature(channel_img, kernel, feature)
    if data is None:
        return False  # not similar
    if data[constants.SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory(fmm, {constants.FEATURE: data[constants.FEATURE]})
        fmm[constants.STATUS] = constants.MATCHED
        update_channel_rank(channel)
        update_kernel_rank(kernel)
    return data[constants.SIMILAR]


# match the experience vision sense
def filter_feature(data, kernel, feature=None):
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


def update_kernel_rank(kernel):
    global used_kernel_rank
    used_kernel_rank = util.update_rank_list(constants.KERNEL, kernel, used_kernel_rank)


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
    used_degrees_rank = util.update_rank_list(constants.DEGREES, degrees, used_degrees_rank)


def get_degrees():
    degrees = util.get_top_rank(used_degrees_rank)
    if degrees is None:
        degrees = random.randint(1, 36)
    return degrees


def update_speed_rank(speed):
    global used_speed_rank
    used_speed_rank = util.update_rank_list(constants.SPEED, speed, used_speed_rank)


def get_speed():
    speed = util.get_top_rank(used_speed_rank)
    if speed is None:
        speed = random.randint(1, 40)
    return speed


def update_channel_rank(channel):
    global used_channel_rank
    used_channel_rank = util.update_rank_list(constants.CHANNEL, channel, used_channel_rank)


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
    mem = search_memory(channel, kernel, data[constants.FEATURE])
    if mem is None:
        mem = memory.add_vision_feature_memory(constants.VISION_FEATURE, channel, kernel, data[constants.FEATURE])
        update_memory_indexes(channel, kernel, mem[constants.ID])
    update_kernel_rank(kernel)
    update_channel_rank(channel)
    return mem


def update_memory_indexes(channel, kernel, mid):
    global memory_indexes
    element = next((x for x in memory_indexes if x[constants.KERNEL] == kernel and x[constants.CHANNEL] == channel),
                   None)
    if element is None:
        new_kernel = {constants.CHANNEL: channel, constants.KERNEL: kernel, MEMORIES: [mid]}
        memory_indexes = np.append(memory_indexes, new_kernel)
    else:
        memory_ids = element[MEMORIES]
        if mid not in memory_ids:
            memory_ids.append(mid)


# search memory by kernel using index
def search_memory(channel, kernel, feature1):
    global memory_indexes
    element = next((x for x in memory_indexes if x[constants.KERNEL] == kernel and x[constants.CHANNEL] == channel),
                   None)
    if element is not None:
        memory_ids = element[MEMORIES]
        live_memories = memory.get_live_memories(memory_ids)
        if live_memories is not None:
            for mem in live_memories:
                feature2 = mem[constants.FEATURE]
                difference = util.np_array_diff(feature1, feature2)
                if difference < FEATURE_SIMILARITY_THRESHOLD:
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
    return int(round(degrees / float(constants.ACTUAL_DEGREES_TIMES)))


def calculate_action(action):
    elapse = time.time() - action[CREATE_TIME]
    # actual degrees is 10 times
    degrees = action[constants.DEGREES] * constants.ACTUAL_DEGREES_TIMES
    # actual speed is 50 times
    speed = action[constants.SPEED] * constants.ACTUAL_SPEED_TIMES
    new_start_y = current_block[START_Y] + (math.sin(math.radians(degrees)) * elapse * speed)
    new_start_x = current_block[START_X] + (math.cos(math.radians(degrees)) * elapse * speed)
    current_block[START_X] = calculate_start_x(new_start_x)
    current_block[START_Y] = calculate_start_y(new_start_y)
    if time.time() > (action[CREATE_TIME] + action[constants.DURATION]):
        action.update({STATUS: COMPLETED})


def calculate_block_histogram(img):
    block_histogram = []
    width = screen_width / NUMBER_SUB_REGION
    height = screen_height / NUMBER_SUB_REGION
    for j in range(0, NUMBER_SUB_REGION):
        for i in range(0, NUMBER_SUB_REGION):
            ret = img[j * height:(j + 1) * height, i * width:(i + 1) * width]
            hist_np, bins = np.histogram(ret.ravel(), bins=27, range=[0, 256])
            block_histogram.append(hist_np)
    return block_histogram


def find_most_variable_region(full_img):
    new_block = {}
    this_block_histogram = calculate_block_histogram(full_img)
    global previous_block_histogram
    if len(previous_block_histogram) == 0:
        previous_block_histogram = this_block_histogram
        return None
    else:
        diff_arr = util.np_matrix_diff(this_block_histogram, previous_block_histogram)
        previous_block_histogram = this_block_histogram
        max_index = np.argmax(diff_arr)
        max_var = diff_arr[max_index]
        if max_var < IMAGE_VARIANCE_THRESHOLD:
            return None
        width = screen_width / NUMBER_SUB_REGION
        height = screen_height / NUMBER_SUB_REGION
        new_index_x, new_index_y = util.convert_1d_to_2d_index(max_index, NUMBER_SUB_REGION)
        new_start_x = new_index_x * width
        new_start_y = new_index_y * height
        new_block[START_X] = calculate_start_x(new_start_x)
        new_block[START_Y] = calculate_start_y(new_start_y)
        new_block.update({'v': max_var})
        previous_block_histogram = this_block_histogram
    return new_block


def aware():
    duration = get_duration()
    full_img = ImageGrab.grab()
    block = find_most_variable_region(full_img)
    if block['v'] > IMAGE_VARIANCE_THRESHOLD:
        # move focus to variable region
        set_movement_absolute(block, duration)


def zoom_in():
    global roi_index
    temp_index = roi_index - 1
    if temp_index < 0:
        return None
    roi_index = temp_index
    return ZOOM_IN


def zoom_out():
    global roi_index
    temp_index = roi_index + 1
    if temp_index > (len(ROI_ARR) - 1):
        return None
    temp_width = ROI_ARR[temp_index]
    if current_block[START_X] + temp_width > screen_width:
        return None
    if current_block[START_Y] + temp_width > screen_height:
        return None
    roi_index = temp_index
    return ZOOM_OUT


def random_zoom():
    ri = random.randint(0, 1)
    if ri == 0:
        zoom_type = zoom_in()
    else:
        zoom_type = zoom_out()
    if zoom_type is None:
        return None
    action = {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_ZOOM, constants.ZOOM_TYPE: zoom_type}
    mem = db.search_vision_zoom(zoom_type)
    if mem is None:
        action_memory = db.add_memory(action)
    else:
        memory.recall_memory(mem)
        action_memory = mem
    slice_memory = memory.add_slice_memory([action_memory])
    return slice_memory


def set_movement_absolute(new_block, duration):
    degrees = calculate_degrees(new_block)
    length = math.hypot(new_block[START_Y] - current_block[START_Y], new_block[START_X] - current_block[START_X])
    speed = length / duration / constants.ACTUAL_SPEED_TIMES
    set_movement_relative(degrees, speed, duration)


def set_movement_relative(degrees, speed, duration):
    global current_action
    action = {constants.DEGREES: degrees, constants.SPEED: speed, constants.DURATION: duration,
              constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE}
    mem = db.search_vision_movement(degrees, speed, duration)
    if mem is None:
        action_memory = db.add_memory(action)
    else:
        memory.recall_memory(mem)
        action_memory = mem
    slice_memory = memory.add_slice_memory([action_memory])
    current_action = copy.deepcopy(action)
    current_action.update({CREATE_TIME: time.time(), STATUS: IN_PROGRESS})
    return slice_memory


def random_move():
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


def explore():
    ri = random.randint(0, 1)
    if ri == 0:
        return random_move()
    else:
        return random_zoom()


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
