import time, random, util, status
import numpy as np

ID = 'id'
STRENGTH = 'str'
RECALL = 'rcl'
REWARD = 'rwd'
LAST_RECALL = 'lrc'
PARENT_MEM = 'pmy'
DURATION = 'drt'
INTERVALS = 'itv'
HAPPEN_TIME = 'hpt'
NEW_MEMORIES = 'nmm'
REST_OF_MEMORIES = 'rom'
COMPOSE_NUMBER = 4

FEATURE_TYPE = 'ftt'
# feature memories
SOUND = 'snd'
VISION = 'vsn'
ACTION = 'fca'
ACTOR = 'atr'
SPEAK = 'spk'

MEMORY_DURATION = 'mmd'
SLICE_MEMORY = '4slm'  # slice memory
INSTANT_MEMORY = '5itm'  # instant memory
SHORT_MEMORY = '6stm'  # short time memory
LONG_MEMORY = '7ltm'  # long time memory

# data set of 'long/short/instant time memory', slice memory
CHILD_MEM = 'cmy'
# additional data
CHILD_DAT1 = 'cd1'
KERNEL = 'knl'
FEATURE = 'ftr'
SIMILAR = 'sml'

# for expectation
STATUS = 'sts'
NEW = '7new'
MATCHING = '6mcg'
MATCHED = '5mcd'
EXPIRED = '4xpd'
START_TIME = 'stt'
END_TIME = 'edt'
DURATION_SLICE = 0.15
DURATION_INSTANT = 0.5
DURATION_SHORT = 3
DURATION_LONG = 360

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
BASIC_MEMORY = {STRENGTH: 0, RECALL: 0, REWARD: 0, LAST_RECALL: 0, PARENT_MEM: [], CHILD_MEM: []}

BASIC_MEMORY_GROUP_DICT = {SLICE_MEMORY: {}, SHORT_MEMORY: {}, INSTANT_MEMORY: {}, LONG_MEMORY: {}}
BASIC_MEMORY_GROUP_ARR = {SLICE_MEMORY: [], SHORT_MEMORY: [], INSTANT_MEMORY: [], LONG_MEMORY: []}

# The first recall time, if less than 60 seconds, memory strength is 100%, and then 99% for 61 seconds ... 21% for 35 days
# TIME_SEC = [60, 61, 63, 66, 70, 75, 81, 88, 96, 105, 115, 126, 138, 151, 165, 180, 196, 213, 231, 250, 270, 291, 313, 336, 360, 385, 411, 438, 466, 495, 525, 540, 600, 660, 720,
#             780, 840, 900, 960, 1020, 1080, 1140, 1200, 1260, 1320, 1440, 1560, 1740, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440, 14040, 18720,
#             24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600, 537840, 853200, 1326240, 2035800, 3100140,
#             3609835, 4203316, 4894372, 5699043, 6636009, 7727020, 8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033, 41225925,
#             48003823, 55896067, 65085866]
TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296, 326,
            358, 392, 428, 466, 506, 548, 593, 641, 692, 746,
            803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367, 1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640,
            2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440, 14040, 18720,
            24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600, 537840, 853200,
            1326240, 2035800, 3100140,
            3609835, 4203316, 4894372, 5699043, 6636009, 7727020, 8997403, 10476649, 12199095, 14204727, 16540102,
            19259434, 22425848, 26112847, 30406022, 35405033, 41225925,
            48003823, 55896067, 65085866]

threshold_of_working_memories = 20


# longer time elapsed, easier to forget
# more times recall, harder to forget
# can not recall frequently in short time
# check result, if memory.strength = -1, that it's forgot
def refresh(mem, recall=False, forget=False):
    deleted = False
    time_elapse = time.time() - mem[LAST_RECALL]
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
                if forget:
                    ran = random.randint(1, 100)
                    if ran > strength:
                        mem[STRENGTH] = -1
                        deleted = True
                        break
                    if len(mem[CHILD_MEM]) <= 0:
                        mem[STRENGTH] = -1
                        deleted = True
                        break
                # if this is recall, will update recall count and last recall time
                if recall:
                    mem[RECALL] = mem[RECALL] + 1
                    mem[LAST_RECALL] = time.time()
            break
    return deleted


# summarize all parent memories in a list
def count_parent_id(memories):
    parent_list = []
    for mem in memories:
        parent_list += mem[PARENT_MEM]
    return util.list_element_count(parent_list)


def find_max_related_memories(memories, tobe_remove_list_ids, limit=4):
    related_memories = []
    parent_counts = count_parent_id(memories)
    count = 0
    for key in sorted(parent_counts, key=parent_counts.get, reverse=True):
        mem = db.get_memory(key)
        if mem:
            related_memories.append(mem)
            count = count + 1
        else:
            tobe_remove_list_ids.append(key)
        if count >= limit:
            break
    return related_memories


def find_update_max_related_memories(memories, limit=4):
    tobe_remove_list_ids = []
    related_memories = find_max_related_memories(memories, tobe_remove_list_ids, limit)
    if len(tobe_remove_list_ids) > 0:
        for mem in memories:
            remove_dead_memories(PARENT_MEM, mem[PARENT_MEM], tobe_remove_list_ids, mem[ID])
    return related_memories


def remove_dead_memories(field, sub_ids, forgot_ids, mid):
    new_sub = util.list_comprehension_new(sub_ids, forgot_ids)
    if field == CHILD_MEM and len(new_sub) == 0:
        db.remove_memory(mid)
    else:
        db.update_memory({field: new_sub}, mid)


def get_live_memories(memory_ids):
    memories = []
    for mid in memory_ids:
        mem = db.get_memory(mid)
        if mem is not None:
            memories.append(mem)


def get_live_sub_memories(mem, field, limit=0, offset=0):
    memory_ids = mem[field]
    forgot_ids = []
    memories = []
    count = 0
    total = limit
    if total == 0:
        total = len(memory_ids)
    for i in range(offset, total):
        sub_id = memory_ids[i]
        sub_mem = db.get_memory(sub_id)
        if sub_mem is not None:
            memories.append(sub_mem)
        else:
            forgot_ids.append(sub_id)
            print "forgot something"
        count = count + 1
        if count >= total:
            break
    if len(forgot_ids) > 0:
        remove_dead_memories(CHILD_MEM, memory_ids, forgot_ids, mem[ID])
    if len(memories) == 0:
        db.remove_memory(mem[ID])
    return memories


def search_sub_memories(memories, distinct_sub_memory_list, sub_memory_dict):
    sub_memory_ids = []
    for smm in memories:
        live_children = get_live_sub_memories(smm, CHILD_MEM)
        sub_memory_dict.update({smm[ID]: live_children})
        for lmm in live_children:
            if lmm[ID] not in sub_memory_ids:
                distinct_sub_memory_list.append(lmm)
                sub_memory_ids.append(lmm[ID])


def recall_memory(mem, addition=None):
    refresh(mem, True, False)
    update_content = {STRENGTH: mem[STRENGTH], RECALL: mem[RECALL], LAST_RECALL: mem[LAST_RECALL]}
    if addition is not None:
        update_content.update(addition)
    db.update_memory(update_content, mem[ID])


# children is list of group memories [[m1, m2], [m3, m4]]
def create_working_memory(seq_time_memories, children, duration_type):
    for memories in children:
        child_memory_ids = [mem[ID] for mem in memories]
        child_memory_rewards = [mem[REWARD] for mem in memories]
        new_reward = np.max(np.array(child_memory_rewards))
        new_mem = db.add_memory(
            {CHILD_MEM: child_memory_ids, MEMORY_DURATION: duration_type, HAPPEN_TIME: time.time(), REWARD: new_reward})
        seq_time_memories[duration_type].append(new_mem)


# slice memories of 4 (COMPOSE_NUMBER) or within DURATION_INSTANT will be grouped as a new instant memory
# instant memories of 4 (COMPOSE_NUMBER) or within DURATION_SHORT will be grouped as a new short memory
# short memories of 4 (COMPOSE_NUMBER) or within DURATION_LONG will be grouped as a new long memory
def compose(seq_time_memories):
    result1 = split_seq_time_memories(seq_time_memories[SLICE_MEMORY], DURATION_INSTANT)
    seq_time_memories[SLICE_MEMORY] = result1[REST_OF_MEMORIES]
    create_working_memory(seq_time_memories, result1[NEW_MEMORIES], INSTANT_MEMORY)

    result2 = split_seq_time_memories(seq_time_memories[INSTANT_MEMORY], DURATION_SHORT)
    seq_time_memories[INSTANT_MEMORY] = result2[REST_OF_MEMORIES]
    create_working_memory(seq_time_memories, result2[NEW_MEMORIES], SHORT_MEMORY)

    result3 = split_seq_time_memories(seq_time_memories[SHORT_MEMORY], DURATION_LONG)
    seq_time_memories[SHORT_MEMORY] = result3[REST_OF_MEMORIES]
    create_working_memory(seq_time_memories, result3[NEW_MEMORIES], LONG_MEMORY)

    result4 = split_seq_time_memories(seq_time_memories[LONG_MEMORY])
    seq_time_memories[LONG_MEMORY] = result4[REST_OF_MEMORIES]
    create_working_memory(seq_time_memories, result4[NEW_MEMORIES], LONG_MEMORY)


# split memory array to certain groups by number or elapse time
# new memories can be found in NEW_MEMORIES of result
# distance of each child memory can be found in CHILD_DAT1 of result
# rest of memories that are not composed can be found in REST_OF_MEMORIES of result
def split_seq_time_memories(memories, gap=60.0):
    count = 0
    last_time = 0
    elapse_time = 0
    groups = []
    group = []
    add_datas = []
    add_data = []
    for mem in memories:
        this_time = mem[HAPPEN_TIME]
        if last_time == 0:
            distance = 0
        else:
            distance = this_time - last_time
        elapse_time = elapse_time + distance
        last_time = mem[HAPPEN_TIME]
        if elapse_time >= gap:
            groups.append(group)
            group = []
            add_datas.append(add_data)
            add_data = []
            count = 0
            elapse_time = 0
        group.append(mem)
        add_data.append(distance)
        count = count + 1
        if count >= COMPOSE_NUMBER:
            groups.append(group)
            group = []
            count = 0
            elapse_time = 0
    result = {
        NEW_MEMORIES: groups,
        CHILD_DAT1: add_datas,
        REST_OF_MEMORIES: group
    }
    return result


def convert_to_expectation(mem):
    exp = {STATUS: MATCHING, START_TIME: time.time()}
    if mem[MEMORY_DURATION] is INSTANT_MEMORY:
        exp.update({END_TIME: time.time() + DURATION_INSTANT})
    elif mem[MEMORY_DURATION] is SHORT_MEMORY:
        exp.update({END_TIME: time.time() + DURATION_SHORT})
    elif mem[MEMORY_DURATION] is LONG_MEMORY:
        exp.update({END_TIME: time.time() + DURATION_LONG})
    elif mem[MEMORY_DURATION] is SLICE_MEMORY:
        exp.update({END_TIME: time.time() + DURATION_SLICE})
    mem.update(exp)


def update_last_recall(memories):
    for mem in memories:
        db.update_memory({LAST_RECALL: time.time()}, mem[ID])


# append new memories to memories list if it's not exist
def append_working_memories(memories, new_memories, limit=0):
    total = 0
    ids = [x[ID] for x in memories]
    sub_ids = [x[ID] for x in new_memories]
    exist = util.list_common(ids, sub_ids)
    total = total + len(exist)
    for nmem in new_memories:
        if total >= limit > 0:
            break
        if nmem[ID] not in ids:
            convert_to_expectation(nmem)
            # higher priority to stay in working memory
            update_last_recall([nmem])
            memories.append(nmem)
            total = total + 1


def associate(working_memories):
    valid_working_memories = [mem for mem in working_memories if mem[END_TIME] > time.time()]
    matched_memories = [mem for mem in valid_working_memories if mem[STATUS] is MATCHED]
    related_memories = find_update_max_related_memories(matched_memories)
    append_working_memories(valid_working_memories, related_memories)
    sorted_working_memories = sorted(valid_working_memories, key=lambda x: (x[LAST_RECALL], x[REWARD]), reverse=True)
    return sorted_working_memories[0:threshold_of_working_memories:]


def prepare_expectation(working_memories):
    pending_memories = [mem for mem in working_memories if mem[STATUS] is MATCHING]
    for pmem in pending_memories:
        live_children = get_live_sub_memories(pmem, CHILD_MEM)
        if pmem[MEMORY_DURATION] is INSTANT_MEMORY:
            append_working_memories(working_memories, live_children)
        elif pmem[MEMORY_DURATION] is LONG_MEMORY or pmem[MEMORY_DURATION] is SHORT_MEMORY:
            append_working_memories(working_memories, live_children, 1)


def check_expectation(working_memories, sequential_time_memories):
    pending_memories = [mem for mem in working_memories if mem[STATUS] is MATCHING]
    for pmem in pending_memories:
        if time.time() > pmem[END_TIME]:
            pmem[STATUS] = EXPIRED
            continue
        all_matched = True
        child_ids = pmem[CHILD_MEM]
        for wmem in working_memories:
            if wmem[ID] in child_ids:
                if wmem[STATUS] is not MATCHED:
                    all_matched = False
                    break
        if all_matched:
            recall_memory(pmem)
            pmem[STATUS] = MATCHED
            pmem[HAPPEN_TIME] = time.time()
            sequential_time_memories[pmem[MEMORY_DURATION]].append(pmem)


# matched / elder / child memory will be higher priority to clean up
# pending / newer / parent / high reward memory will be lower priority to clean up
# this is most important for making decision (what's next expectation)
# pure memory recall (when free) will impact this, which it is "thinking"
# interruption from environment can impact this, which it is "disturb"
def cleanup_working_memories(working_memories, work_status):
    valid_working_memories = [mem for mem in working_memories if mem[END_TIME] > time.time()]
    if work_status[status.REWARD]:
        sorted_working_memories = sorted(valid_working_memories,
                                         key=lambda x: (x[MEMORY_DURATION], x[STATUS], x[LAST_RECALL], x[REWARD]),
                                         reverse=True)
    else:
        # not satisfy, reward first
        sorted_working_memories = sorted(valid_working_memories,
                                         key=lambda x: (x[REWARD], x[MEMORY_DURATION], x[STATUS], x[LAST_RECALL]),
                                         reverse=True)
    return sorted_working_memories[0:threshold_of_working_memories:]


def add_feature_memory(feature_type, kernel, feature):
    db.add_memory({FEATURE_TYPE: feature_type, KERNEL: kernel, FEATURE: feature})


def add_action_memory(addition=None):
    db.add_action(addition)


def add_slice_memory(child_memories):
    child_memory_ids = [x[ID] for x in child_memories]
    db.add_memory({CHILD_MEM: child_memory_ids, MEMORY_DURATION: SLICE_MEMORY})


def verify_slice_memory_match_result(slice_memories, slice_memory_children):
    all_matched_feature_memories = []
    ids = []
    for smm in slice_memories:
        smm_all_matched = True
        live_children = slice_memory_children.get(smm[ID])
        for fmm in live_children:
            if fmm[STATUS] is MATCHED:
                if fmm[ID] not in ids:
                    all_matched_feature_memories.append(fmm)
                    ids.append(fmm[ID])
            else:
                smm_all_matched = False
        if smm_all_matched:
            smm[STATUS] = MATCHED
            recall_memory(smm)
    return all_matched_feature_memories
