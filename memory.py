import time, random, util

STRENGTH = 'str'
RECALL = 'rcl'
REWARD = 'rwd'
LASTRECALL = 'lrc'
PARENTS = 'prt'
DURATION= 'drt'
INTERVALS='itv'

TYPE = 'typ'
# below are memory types
COLLECTION = 'clt'  # non physical memory,
# physical memories
SOUND = 'snd'
VISION = 'vsn'
FOCUS = 'fcs'
SPEAK = 'spk'

TYPE_COLLECTION = 'toc'  # type of collection
# below are types of collection
INSTANT_MEMORY = 'itm'  # instant memory
SHORT_MEMORY = 'stm'  # short time memory
LONG_MEMORY = 'ltm'  # long time memory
SLICE_MEMORY = 'slm' # slice memory

# data set of 'long/short/instant time memory', slice memory
CHILD_DATA = 'cdt'

#                                                                                                                                                                                  collections
#                                                                                                                                        long                                   long            ...       long
#                                                                                 short                                               short       ...       short
#                             instant                                          instant         ...         instant
# slice1        slice2      slice3      slice4      slice5 (max5)
# vision1.1   vision2   vision3     vision4     vision5
# sound1      sound2
# vision1.2


db = None

# use parent to find experience memories
BASIC_MEMORY = {STRENGTH: 0, RECALL: 0, REWARD: 0, LASTRECALL: 0, PARENTS: []}

# The first recall time, if less than 60 seconds, memory strength is 100%, and then 99% for 61 seconds ... 21% for 35 days
# TIME_SEC = [60, 61, 63, 66, 70, 75, 81, 88, 96, 105, 115, 126, 138, 151, 165, 180, 196, 213, 231, 250, 270, 291, 313, 336, 360, 385, 411, 438, 466, 495, 525, 540, 600, 660, 720,
#             780, 840, 900, 960, 1020, 1080, 1140, 1200, 1260, 1320, 1440, 1560, 1740, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440, 14040, 18720,
#             24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600, 537840, 853200, 1326240, 2035800, 3100140,
#             3609835, 4203316, 4894372, 5699043, 6636009, 7727020, 8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033, 41225925,
#             48003823, 55896067, 65085866]
TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296, 326, 358, 392, 428, 466, 506, 548, 593, 641, 692, 746,
            803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367, 1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440, 14040, 18720,
            24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600, 537840, 853200, 1326240, 2035800, 3100140,
            3609835, 4203316, 4894372, 5699043, 6636009, 7727020, 8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033, 41225925,
            48003823, 55896067, 65085866]

forget_memory = True


# longer time elapsed, easier to forget
# more times recall, harder to forget
# can not recall frequently in short time
# check result, if memory.strength = -1, that it's forgot
def refresh(mem, recall=False):
    deleted = False
    time_elapse = time.time() - mem[LASTRECALL]
    if time_elapse < TIME_SEC[0]:
        return deleted
    count = 0
    for num in range(mem[RECALL], len(TIME_SEC)):
        if TIME_SEC[num] <= time_elapse:
            count = count + 1
        else:
            strength = 100 - count
            mem[STRENGTH] = strength
            if count > 0:
                # random forget memory base on strength
                if forget_memory:
                    ran = random.randint(1, 100)
                    if ran > strength:
                        mem[STRENGTH] = -1
                        deleted = True
                        break
                # if this is recall, will update recall count and last recall time
                if recall:
                    mem[RECALL] = mem[RECALL] + 1
                    mem[LASTRECALL] = time.time()
            break
    return deleted


# TODO, need to check if parent memory is valid or not
# summarize all parent memories in a list
def find_parents(working_memories):
    parent_list = []
    for mem in working_memories:
        parent_list += mem[PARENTS]
    return util.list_element_count(parent_list)


# find out max occurrence in parent memories of all working memories
# if all occur once, return [] (not found)
# only search when working memories >2
def find_related_memory_ids(working_memories):
    parent_counts = find_parents(working_memories)
    max_value = 0
    max_ids = []
    max_count = 0
    for key, value in parent_counts.items():
        if value > max_count:
            max_value = value
            max_count = max_count + 1
    if max_count == 1:
        max_ids = []
    else:
        for key, value in parent_counts.items():
            if value == max_value:
                max_ids.append(key)
    return max_ids


# find max reward in memories (db record), this is the target
def find_reward_target(related_memories):
    max_value = 0
    max_id = 0
    for mem in related_memories:
        reward = mem[REWARD]
        if reward > max_value:
            max_value = reward
            max_id = mem.doc_id
    return max_id


# TODO, can enhance?
def remove_memories(memory_list, tobe_remove_list_ids):
    for el in tobe_remove_list_ids:
        for mem in memory_list:
            if mem.doc_id in tobe_remove_list_ids:
                memory_list.remove(mem)


# check if can combine small feature memories to larger parent memory
# if match a parent memory, will add to return list, and remove from feature memories
def find_common_parents(feature_memories):
    common_parents = []
    if len(feature_memories) <= 1:
        return common_parents
    parent_ids = find_parents(feature_memories)
    feature_memory_ids = []
    for feature in feature_memories:
        feature_memory_ids.append(feature.doc_id)
    for key, value in parent_ids.items():
        if value <= 1:
            continue
        mem = db.use_memory(key)
        if mem is None:
            continue
        print 'found exp memory ', mem.doc_id
        first_data = mem[CHILD_DATA]
        first_common = util.common_elements(first_data, feature_memory_ids)
        # check if this parent memory all matches
        if len(first_common) == len(first_data):
            common_parents.append(mem)
            remove_memories(feature_memories, first_common)
    return common_parents
