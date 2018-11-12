import time, cv2, util, memory, status, copy, random, math
from PIL import ImageGrab, Image
from win32api import GetSystemMetrics
from scipy import ndimage
import numpy as np

inited = False
db = None

# 1920	960	320	80	16
# 1080	540	180	45	9
screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)
roi_arr = [9, 18, 36, 72, 144, 288]
ROI_LEVEL = 3
current_pivot = None
X = 'x'
Y = 'y'
NUMBER_SUB_REGION = 10
INPUT_SIZE = 9
SIMILARITY_THRESHOLD = 0.9
VARIANCE_THRESHOLD = 0.3
FEATURE_MAP_SIZE = 3

KERNEL = 'knl'
FEATURE = 'ftr'
SIMILAR = 'sml'
FEATURE_DATA = {KERNEL: [], FEATURE: [], SIMILAR: False}
CHANNEL = 'cnl'
USED_COUNT = 'uct'
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
VISION_KERNEL_FILE = 'vision_kernels90.npy'
used_speed_rank = None
used_degrees_rank = None
used_kernel_rank = None
sound_kernels = None
previous_energies = []
previous_block_histogram = []


def init():
    global inited
    if inited is False:
        global current_pivot
        pos_x = screen_width / 2
        pos_y = screen_height / 2
        current_pivot = {X: pos_x, Y: pos_y}

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
            used_kernel_rank = {}

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


def process(working_memories, work_status, sequential_time_memories):
    init()
    global current_action
    if current_action[STATUS] is IN_PROGRESS:
        calculate_action(current_action)

    slice_memories = [mem for mem in working_memories if
                      mem[memory.MEMORY_DURATION] is memory.SLICE_MEMORY and mem[memory.FEATURE_TYPE] is memory.VISION]

    matched_feature_memories = match(slice_memories)

    new_feature_memory = look()
    if len(matched_feature_memories) > 0:
        matched_feature_memories.append(new_feature_memory)
        new_slice_memory = memory.add_slice_memory(matched_feature_memories)
        sequential_time_memories[memory.SLICE_MEMORY].append(new_slice_memory)
    else:
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


def watch(fmm):
    kernel = fmm[memory.KERNEL]
    feature = fmm[memory.FEATURE]
    fmm.update({memory.STATUS: memory.MATCHING})
    img = get_region()
    data = filter_feature(img, kernel, feature)
    if data[SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory(fmm, {FEATURE: data[FEATURE]})
        fmm[memory.STATUS] = memory.MATCHED
    return data[SIMILAR]


# match the experience vision sense
def filter_feature(data, kernel, feature=None):
    feature_data = copy.deepcopy(FEATURE_DATA)
    feature_data[KERNEL] = kernel
    # TODO
    cov = cv2.filter2D(data, -1, kernel)
    # TODO
    new_feature = ndimage.maximum_filter(cov, size=FEATURE_MAP_SIZE)
    if feature is None:
        feature_data[FEATURE] = new_feature
    else:
        similarity = util.compare_feature(new_feature, feature)
        feature_data[SIMILAR] = True
        if similarity > SIMILARITY_THRESHOLD:
            new_feature = (feature + new_feature) / 2
        feature_data[FEATURE] = new_feature
    return feature_data


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


# try to find more detail
def look():
    ri = random.randint(1, 3)
    channel = 'y'
    if ri == 1:
        channel = 'u'
    elif ri == 2:
        channel = 'v'

    img = get_region()
    kernel = get_kernel()
    data = filter_feature(img, kernel)
    kernel_id = channel + '-' + kernel
    mem = search_memory(kernel_id, data[FEATURE])
    if mem is None:
        mem = memory.add_feature_memory(memory.VISION, kernel, data[FEATURE])
        vision_kernel = {CHANNEL: channel, KERNEL: kernel, USED_COUNT: 1, LAST_USED_TIME: time.time(),
                         MEMORIES: [mem[memory.ID]]}
        used_kernel_rank.update({kernel_id: vision_kernel})
    return mem


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


def calculate_action(action):
    elapse = time.time() - action[CREATE_TIME]
    # TODO
    new_pivot_y = current_pivot[Y] - (math.sin(action[DEGREES]) * elapse * action[SPEED])
    new_pivot_x = current_pivot[X] + (math.cos(action[DEGREES]) * elapse * action[SPEED])
    if new_pivot_x > screen_width:
        new_pivot_x = screen_width
    if new_pivot_y > screen_height:
        new_pivot_y = screen_height
    current_pivot[X] = new_pivot_x
    current_pivot[Y] = new_pivot_y
    if time.time() > (action[CREATE_TIME] + action[DURATION]):
        action.update({STATUS: COMPLETED})


def calculate_degrees(new_pivot):
    radians = math.atan2(new_pivot[Y] - current_pivot[Y], new_pivot[X] - current_pivot[X])
    degrees = math.degrees(radians)
    return degrees


def find_most_variable_region():
    new_pivot = {}
    this_block_histogram = []
    full_img = ImageGrab.grab()
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
        new_pivot[X] = max_index % NUMBER_SUB_REGION + width
        new_pivot[Y] = max_index / NUMBER_SUB_REGION + height
        new_pivot.update({'v': max_var})
        previous_block_histogram = this_block_histogram
    return new_pivot


def aware():
    duration = get_duration()
    pivot = find_most_variable_region()
    if pivot['v'] > VARIANCE_THRESHOLD:
        # move focus to variable region
        move_absolute(pivot, duration)


def get_degrees():
    global used_degrees_rank
    if len(used_degrees_rank) > 0:
        return used_degrees_rank[0]
    else:
        return random.randint(1, 360)


def get_speed():
    global used_speed_rank
    if len(used_speed_rank) > 0:
        return used_speed_rank[0]
    else:
        return random.randint(1, 4000)


def get_duration():
    return random.randint(1, 5) / 10.0


def move_absolute(new_pivot, duration):
    degrees = calculate_degrees(new_pivot)
    length = math.hypot(new_pivot[Y] - current_pivot[Y], new_pivot[X] - current_pivot[X])
    speed = length / duration
    move_relative(degrees, speed, duration)


def move_relative(degrees, speed, duration):
    global current_action
    current_action = {DEGREES: degrees, SPEED: speed, DURATION: duration}
    current_action.update({memory.ACTOR: memory.VISION})
    action_memory = memory.add_action_memory(current_action)
    slice_memory = memory.add_slice_memory([action_memory[memory.ID]])
    return slice_memory


def explore():
    # random move, explore the world
    degrees = get_degrees()
    # most frequent speed
    speed = get_speed()
    # 0.1-0.5s
    duration = get_duration()
    slice_memory = move_relative(degrees, speed, duration)
    return slice_memory


def get_region():
    half_width = roi_arr[ROI_LEVEL] / 2
    pos_x = current_pivot[X] - half_width
    pos_y = current_pivot[Y] - half_width
    roi_image = crop(ROI_LEVEL, pos_x, pos_y)
    cv_img = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2BGR)
    img = cv2.resize(cv_img, (INPUT_SIZE, INPUT_SIZE))
    return img


# grab and crop a fix size region with specified zoom level from screen
# x1,y1 is starting position (left top)
def crop(level, x1, y1):
    if x1 >= screen_width or y1 >= screen_height:
        return None
    x2 = x1 + roi_arr[level]
    y2 = y1 + roi_arr[level]
    new_width = roi_arr[level]
    new_height = roi_arr[level]
    if x2 > screen_width:
        new_width = (screen_width - x1) / level
        x2 = screen_width
    if y2 > screen_height:
        new_height = (screen_height - y1) / roi_arr[level]
        y2 = screen_height
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    if level > 1:
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
    return img
