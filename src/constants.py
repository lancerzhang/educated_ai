# feature types
speech = 'Speech'
vision = 'Vision'
feature_types = [speech]

# memory types
feature = 'feature'
pack = 'Pack'  # one pack memory can contains multiple features
temporal = 'Temporal'  # temporal memories
memory_types = [feature, pack, temporal]
memory_duration = [0, 0.3, 7]

stable = 3
n_memory_children = 3
n_memory_context = 10

# vision
ZOOM_TYPE = 'zmt'
ZOOM_DIRECTION = 'zdt'
DEGREES = 'dgr'
SPEED = 'spd'
MOVE_DURATION = 'drt'
# ACTUAL_SPEED_TIMES = 50
# ACTUAL_DEGREES_TIMES = 10

# memory
ID = '_id'
MID = 'mid'
STRENGTH = 'str'
RECALL_COUNT = 'rcc'
REWARD = 'rwd'
WORKING_REWARD = 'wrw'
LAST_RECALL_TIME = 'lrt'
PROTECT_TIME = 'ptt'
KERNEL = 'knl'
FEATURE = 'ftr'
SIMILAR = 'sml'
CHANNEL = 'cnl'
PARENT_MEM = 'pmy'
CHILD_MEM = 'cmy'
# PHYSICAL_MEMORY_TYPE = 'pmt'
# SOUND_FEATURE = 'sft'
# VISION_FEATURE = 'vft'
# VISION_FOCUS_MOVE = 'vfm'
# VISION_FOCUS_ZOOM = 'vfz'
# ACTION_MOUSE_CLICK = 'amc'
# ACTION_REWARD = 'arw'
# VIRTUAL_MEMORY_TYPE = 'vmt'
# FEATURE_MEMORY = '3ftr'
# SLICE_MEMORY = '4slm'
# INSTANT_MEMORY = '5itm'  # instant memory
# SHORT_MEMORY = '6stm'  # short time memory
# LONG_MEMORY = '7ltm'  # long time memory
STATUS = 'sts'
# NEW = '7new'
# MATCHING = '6mcg'
# MATCHED = '5mcd'
# LIVING = '4lvn'
# DORMANT = '3dmt'
START_TIME = 'stt'
END_TIME = 'edt'
LAST_ACTIVE_TIME = 'lat'
HAPPEN_TIME = 'hpt'
MEMORIES = 'mms'
COUNT = 'count'

# action
CLICK_TYPE = 'clt'
LEFT_CLICK = 'lcl'
FOCUS_X = 'fcx'
FOCUS_Y = 'mvy'

# main
process_per_second = 10  # adjust according to your process unit
LAST_SYSTEM_TIME = 'lst'

# gc
EDEN = 'eden'
YOUNG = 'young'
OLD = 'old'

# keyboard
KEY_CTRL = 'ctrl'
KEY_ALT = 'alt'
KEY_SHIFT = 'shift'
MOUSE_LEFT = 'mouse_left'

# video file
CURRENT_FRAME = 'current_frame'
FPS = 'fps'
