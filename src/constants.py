# feature types
voice = 'Voice'
image = 'Image'

feature_types = [voice]

# memory types
real = 'Real'  # one real memory
pack = 'Pack'  # pack of one type of real memories happened at the same time
instant = 'Instant'  # pack memories happened in an instant, it's phone in voice
short = 'Short'  # memories happened in a short time, it's word in voice
long = 'Long'  # memories happened in a long time, it's sentence in voice
# long2 = 'Long2'  # memories happened in a longer time, it's sentence in voice
context = 'Context'  # connection between high level memories

memory_types = [real, pack, instant, short, long, context]
memory_duration = [0, 0, 0.5, 5, 20, -1]

ordered = 'Ordered'
unordered = 'Unordered'
stable = 2
n_memory_children = 4
n_memory_context = 10

# memory status
# dormant memories will be clean up in high priority
# dormant memories can't be activated
# dormant memories can be retrieved if it's yet clean up, recall count will be kept
dormant = 'Dormant'
sleep = 'Sleep'
living = 'Living'
matched = 'Matched'
matching = 'Matching'

# vision
ZOOM_TYPE = 'zmt'
ZOOM_DIRECTION = 'zdt'
DEGREES = 'dgr'
SPEED = 'spd'
MOVE_DURATION = 'drt'
# ACTUAL_SPEED_TIMES = 50
# ACTUAL_DEGREES_TIMES = 10

# status
BUSY = 'busy'
SHORT_DURATION = 'S'
MEDIUM_DURATION = 'M'
LONG_DURATION = 'L'

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
