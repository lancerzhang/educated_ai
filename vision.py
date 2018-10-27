import time, cv2, util, numpy, memory, status, copy
from PIL import ImageGrab, Image
from win32api import GetSystemMetrics
from scipy import ndimage

# 1920	960	320	80	16
# 1080	540	180	45	9

POINT_COLOR = 'PC'
IMG_HASH = 'IH'

screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)
pos_x = screen_width / 2
pos_y = screen_height / 2

roi_arr = [9, 18, 36, 72, 144, 288]
roi_level = 3

db = None

INPUT_IMG_SIZE = 9
SIMILARITY_THRESHOLD = 0.9
VARIANCE_THRESHOLD = 0.3
FEATURE_MAP_SIZE = 3
KERNEL = 'kernel'
FEATURE = 'feature'
SIMILAR = 'similar'
FEATURE_DATA = {KERNEL: [], FEATURE: [], SIMILAR: False}
v_filter = {'y-123': {'channel': 'y', 'filter': [], 'used_count': 0, 'last_used_time': 0, 'memories': {}}}


def start():
    # watch start
    return


def match(slice_memories):
    distinct_feature_memories = []
    slice_memory_children = {}
    memory.get_live_children(slice_memories, distinct_feature_memories, slice_memory_children)
    for fmm in distinct_feature_memories:
        watch(fmm)
    matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
    return matched_feature_memories


def process(working_memories, work_status, sequential_time_memories):
    slice_memories = [mem for mem in working_memories if mem[memory.MEMORY_DURATION] is memory.SLICE_MEMORY and mem[memory.FEATURE_TYPE] is memory.VISION]

    matched_feature_memories = match(slice_memories)

    new_feature_memory = look()
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

    if not work_status[status.BUSY][status.SHORT_DURATION]:
        aware()

    if not work_status[status.BUSY][status.MEDIUM_DURATION] or not work_status[status.REWARD]:
        explore()


def watch(fmm):
    kernel = fmm[memory.KERNEL]
    feature = fmm[memory.FEATURE]
    fmm.update({memory.STATUS: memory.MATCHING})
    img = get_region()
    data = filter(img, kernel, feature)
    if data[SIMILAR]:
        # recall memory and update feature to average
        memory.recall_memory({FEATURE: data[FEATURE]})
        fmm[memory.STATUS] = memory.MATCHED
    return data[SIMILAR]


# match the experience vision sense
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


def look():
    img = get_region()
    kernel = get_kernel()
    data = filter(img, kernel)
    mem = search_memory(kernel, data[FEATURE])
    if mem is None:
        mem = db.add_vision()
    return mem


def look_for_slice_memory():
    return


def find_most_variable_region():
    return


# search memory by kernel using index
def search_memory(kernel, feature):
    return


def aware():
    img = find_most_variable_region
    variance = 0
    if variance > VARIANCE_THRESHOLD:
        # move focus to variable region
        move()


def explore():
    # random move, expore the world
    move()


def move():
    # move ROI
    return


def zoom():
    # zoom ROI
    return


def get_region():
    roi_image = crop(roi_level, pos_x, pos_y)
    cv_img = cv2.cvtColor(numpy.array(roi_image), cv2.COLOR_RGB2BGR)
    img = cv2.resize(cv_img, (INPUT_IMG_SIZE, INPUT_IMG_SIZE))
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
