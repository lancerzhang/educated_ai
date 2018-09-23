import time, cv2, util, numpy, memory
from PIL import ImageGrab, Image
from win32api import GetSystemMetrics

# 1920	960	320	80	16
# 1080	540	180	45	9

POINT_COLOR = 'PC'
IMG_HASH = 'IH'

screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)
pos_x = screen_width / 2
pos_y = screen_height / 2

roi_arr = [9, 18, 36, 72, 144, 288]
roi_level = 5

hash_size = 3

db = None


def init():
    # watch start
    return;


def watch(hist_short_memories, hist_instant_memories):
    for mem in hist_instant_memories:
        slice = mem.get_slice()
        matched = match(mem)
        if matched:
            remove_others(hist_short_memories, hist_instant_memories)
        else
            remove_itself(hist_short_memories, hist_instant_memories)


# given list of possible slice memory, match from 1st to end, if all not match, return a new one
def match(mem_v):
    # watch frame (0.1s) start
    start = time.time()
    # getROI(); 9x9 ... 288x288, default 72x72
    pil_image = grab(roi_level, pos_x, pos_y)
    opencv_image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)

    # overall color category
    reg_cat = util.point_color_category(opencv_image)
    # hash
    reg_hash = util.image_hash(opencv_image, hash_size)

    # try to watch something match memory
    # it can be feature of ROI, or feature of sub ROI (TODO)
    if mem_v is not None:
        if mem_v.VISION_DATA is not None:
            match = True
            point_color = mem_v.VISION_DATA.PC
            if point_color is not None and point_color != reg_cat:
                match = False
            img_hash = mem_v.VISION_DATA.HSH
            if img_hash is not None and img_hash == reg_hash:
                match = False

            # compare filter

            # compare 9 sub roi, point color, img hash and filter

            # all match, strengthen memory
            if match:
                db.use_memory(mem_v.doc_id)
            else:
                db.add_vision({memory.CHILD_MEM: {POINT_COLOR: reg_cat, IMG_HASH: reg_hash}})
        else:
            mem_v.update({memory.CHILD_MEM: {POINT_COLOR: reg_cat, IMG_HASH: reg_hash}})
    else:
        db.add_vision({memory.CHILD_MEM: {POINT_COLOR: reg_cat, IMG_HASH: reg_hash}})

    # watch frame end
    end = time.time()
    return;


def move():
    # move ROI
    return;


def zoom():
    # zoom ROI
    return;


# grab a fix size region with specified zoom level from screen
# x1,y1 is starting position (left top)
def grab(level, x1, y1):
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


pil_image = grab(roi_level, pos_x, pos_y)
# pil_image.save('screen1.jpg')
# img=numpy.array(img)
opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
# cv2.imshow('img',opencvImage)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
reg_point = cv2.resize(opencvImage, (1, 1))
reg_cat = util.colorSorter(reg_point[0, 0])
print reg_cat
