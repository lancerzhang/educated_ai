import logging
import random
import time

import numpy as np

import constants
import util

logger = logging.getLogger('memory')
logger.setLevel(logging.DEBUG)

INTERVALS = 'itv'
NEW_MEMORIES = 'nmm'
REST_OF_MEMORIES = 'rom'
COMPOSE_NUMBER = 4

# additional data
CHILD_DAT1 = 'cd1'

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


data_adaptor = None

# use parent to find experience memories
BASIC_MEMORY = {constants.STRENGTH: 0, constants.RECALL: 0, constants.REWARD: 0, constants.LAST_RECALL_TIME: 0,
                constants.PARENT_MEM: [], constants.CHILD_MEM: []}

BASIC_MEMORY_GROUP_ARR = {constants.SLICE_MEMORY: [], constants.SHORT_MEMORY: [], constants.INSTANT_MEMORY: [],
                          constants.LONG_MEMORY: []}

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

threshold_of_working_memories = 50


# longer time elapsed, easier to forget
# more times recall, harder to forget
# can not recall frequently in short time
# check result, if memory.strength = -1, that it's forgot
def refresh(mem, recall=False, forget=False):
    is_deleted = False
    now_time = int(time.time())
    time_elapse = now_time - mem[constants.LAST_RECALL_TIME]
    if time_elapse < TIME_SEC[0]:
        return is_deleted
    count = 0
    for num in range(mem[constants.RECALL], len(TIME_SEC)):
        if TIME_SEC[num] <= time_elapse:
            count = count + 1
        else:
            strength = 100 - count
            mem[constants.STRENGTH] = strength
            if count > 0:
                # random forget memory base on strength
                if forget:
                    ran = random.randint(1, 100)
                    if ran > strength:
                        mem[constants.STRENGTH] = -1
                        is_deleted = True
                        break
                    # if not mem.has_key(constants.FEATURE) and len(mem[constants.CHILD_MEM]) <= 0:
                    #     mem[STRENGTH] = -1
                    #     deleted = True
                    #     break
                # if this is recall, will update recall count and last recall time
                if recall:
                    mem[constants.RECALL] = mem[constants.RECALL] + 1
                    mem[constants.LAST_RECALL_TIME] = int(time.time())
            break
    return is_deleted


# summarize all parent memories in a list
def count_parent_id(memories):
    # start = time.time()
    parent_list = []
    for mem in memories:
        # TODO, some memory has hundreds of parent, don't know why
        if len(mem[constants.PARENT_MEM]) < 20:
            parent_list += mem[constants.PARENT_MEM]
    # print len(parent_list)
    parent_count = util.list_element_count(parent_list)
    # print 'count_parent_id used time	' + str(time.time() - start)
    return parent_count


def find_max_related_memories(memories, tobe_remove_list_ids, limit=4):
    # start = time.time()
    related_memories = []
    parent_counts = count_parent_id(memories)
    count = 0
    for key in sorted(parent_counts, key=parent_counts.get, reverse=True):
        mem = data_adaptor.get_memory(key)
        if mem:
            related_memories.append(mem)
            count = count + 1
        else:
            tobe_remove_list_ids.append(key)
        if count >= limit:
            break
    # print 'find_max_related_memories used time	' + str(time.time() - start)
    return related_memories


def find_update_max_related_memories(memories, limit=4):
    # start = time.time()
    tobe_remove_list_ids = []
    related_memories = find_max_related_memories(memories, tobe_remove_list_ids, limit)
    if len(tobe_remove_list_ids) > 0:
        for mem in memories:
            reduce_list_field(constants.PARENT_MEM, mem[constants.PARENT_MEM], tobe_remove_list_ids,
                              mem[constants.MID])
    # print 'find_update_max_related_memories used time	' + str(time.time() - start)
    return related_memories


def increase_list_field(memories, field, new_id):
    for mem in memories:
        ids = mem[field]
        if new_id not in ids:
            ids = util.np_array_concat(ids, [new_id])
            data_adaptor.update_memory({field: ids.tolist()}, mem[constants.MID])


def reduce_list_field(field, sub_ids, forgot_ids, mid):
    new_sub = util.list_comprehension_new(sub_ids, forgot_ids)
    if field == constants.CHILD_MEM and len(new_sub) == 0:
        data_adaptor.remove_memory(mid)
    else:
        data_adaptor.update_memory({field: new_sub}, mid)


def get_live_memories(memory_ids):
    memories = []
    for mid in memory_ids:
        mem = data_adaptor.get_memory(mid)
        if mem is not None:
            memories.append(mem)
    return memories


def get_live_sub_memories(mem, field, existing_memories=None, limit=0, offset=0):
    memory_ids = mem[field]
    forgot_ids = []
    memories = []
    count = 0
    total = limit
    if total == 0:
        total = len(memory_ids)
    for i in range(offset, total):
        sub_id = memory_ids[i]
        sub_mem = None
        if existing_memories is not None:
            for mem in existing_memories:
                if mem[constants.MID] == sub_id:
                    sub_mem = mem
                    memories.append(sub_mem)
                    break
        if sub_mem is None:
            sub_mem = data_adaptor.get_memory(sub_id)
            if sub_mem is not None:
                memories.append(sub_mem)
                if existing_memories is not None:
                    existing_memories.append(sub_mem)
            else:
                forgot_ids.append(sub_id)
                logger.debug('forgot something')
        count = count + 1
        if count >= total:
            break
    if len(forgot_ids) > 0:
        reduce_list_field(constants.CHILD_MEM, memory_ids, forgot_ids, mem[constants.MID])
    if field is constants.CHILD_MEM and len(memories) == 0:
        data_adaptor.remove_memory(mem[constants.MID])
    return memories


def search_sub_memories(memories, distinct_sub_memory_list, sub_memory_dict):
    for smm in memories:
        live_children = get_live_sub_memories(smm, constants.CHILD_MEM, distinct_sub_memory_list)
        sub_memory_dict.update({smm[constants.MID]: live_children})


def recall_feature_memory(mem, feature):
    if isinstance(feature, np.ndarray):
        feature = feature.tolist()
    update_content = {constants.FEATURE: feature}
    recall_memory(mem, update_content)


def recall_memory(mem, addition=None):
    refresh(mem, True, False)
    update_content = {constants.STRENGTH: mem[constants.STRENGTH], constants.RECALL: mem[constants.RECALL],
                      constants.LAST_RECALL_TIME: mem[constants.LAST_RECALL_TIME]}
    if addition is not None:
        update_content.update(addition)
    data_adaptor.update_memory(update_content, mem[constants.MID])
    mem.update({constants.HAPPEN_TIME: time.time()})
    mem.update({constants.LAST_ACTIVE_TIME: time.time()})
    mem.update({constants.STATUS: constants.MATCHED})
    mem.update(update_content)


def remove_duplicate_memory(memories):
    new_memories = []
    new_memories_ids = []
    for mem in memories:
        if mem[constants.MID] not in new_memories_ids:
            new_memories.append(mem)
            new_memories_ids.append(mem[constants.MID])
    return new_memories


# children is list of group memories [[m1, m2], [m3, m4]]
def create_working_memory(working_memories, seq_time_memories, children, duration_type):
    if children is None or len(children) == 0:
        return
    for memories in children:
        if len(memories) > 0:
            child_memories = remove_duplicate_memory(memories)
            child_memory_rewards = [mem[constants.REWARD] for mem in child_memories]
            max_reward = np.max(np.array(child_memory_rewards))
            # new_reward is int32, which will become "\x00\x00\x00\x00" when insert to CodernityDB
            max_reward = int(max_reward)
            new_reward = max_reward - 1
            if new_reward < 0:
                new_reward = 0
            new_mem = add_collection_memory(duration_type, child_memories, reward=new_reward)
            seq_time_memories[duration_type].append(new_mem)
            working_memories.append(new_mem)


# slice memories of 4 (COMPOSE_NUMBER) or within DURATION_INSTANT will be grouped as a new instant memory
# instant memories of 4 (COMPOSE_NUMBER) or within DURATION_SHORT will be grouped as a new short memory
# short memories of 4 (COMPOSE_NUMBER) or within DURATION_LONG will be grouped as a new long memory
def compose(working_memories, seq_time_memories):
    # start = time.time()
    result1 = split_seq_time_memories(seq_time_memories[constants.SLICE_MEMORY], DURATION_INSTANT)
    seq_time_memories[constants.SLICE_MEMORY] = result1[REST_OF_MEMORIES]
    create_working_memory(working_memories, seq_time_memories, result1[NEW_MEMORIES], constants.INSTANT_MEMORY)

    result2 = split_seq_time_memories(seq_time_memories[constants.INSTANT_MEMORY], DURATION_SHORT)
    seq_time_memories[constants.INSTANT_MEMORY] = result2[REST_OF_MEMORIES]
    create_working_memory(working_memories, seq_time_memories, result2[NEW_MEMORIES], constants.SHORT_MEMORY)

    result3 = split_seq_time_memories(seq_time_memories[constants.SHORT_MEMORY], DURATION_LONG)
    seq_time_memories[constants.SHORT_MEMORY] = result3[REST_OF_MEMORIES]
    create_working_memory(working_memories, seq_time_memories, result3[NEW_MEMORIES], constants.LONG_MEMORY)

    result4 = split_seq_time_memories(seq_time_memories[constants.LONG_MEMORY])
    seq_time_memories[constants.LONG_MEMORY] = result4[REST_OF_MEMORIES]
    create_working_memory(working_memories, seq_time_memories, result4[NEW_MEMORIES], constants.LONG_MEMORY)
    # print 'compose used time	' + str(time.time() - start)


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
        if constants.HAPPEN_TIME not in mem:
            logger.error('error memory is {0}'.format(mem))
        this_time = mem[constants.HAPPEN_TIME]
        if last_time == 0:
            distance = 0
        else:
            distance = this_time - last_time
        elapse_time = elapse_time + distance
        last_time = mem[constants.HAPPEN_TIME]
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
    if constants.MEMORY_DURATION not in mem:
        logger.error('error_memory is {0}'.format(mem))
    exp = {constants.STATUS: constants.MATCHING, constants.START_TIME: time.time(),
           constants.LAST_ACTIVE_TIME: time.time()}
    if mem[constants.MEMORY_DURATION] is constants.INSTANT_MEMORY:
        exp.update({constants.END_TIME: time.time() + DURATION_INSTANT})
    elif mem[constants.MEMORY_DURATION] is constants.SHORT_MEMORY:
        exp.update({constants.END_TIME: time.time() + DURATION_SHORT})
    elif mem[constants.MEMORY_DURATION] is constants.LONG_MEMORY:
        exp.update({constants.END_TIME: time.time() + DURATION_LONG})
    elif mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY:
        exp.update({constants.END_TIME: time.time() + DURATION_SLICE})
    mem.update(exp)


def update_last_recall(memories):
    for mem in memories:
        data_adaptor.update_memory({constants.LAST_RECALL_TIME: int(time.time())}, mem[constants.MID])


# append new memories to memories list if it's not exist
def append_working_memories(memories, new_memories, limit=0):
    total = 0
    ids = [x[constants.MID] for x in memories]
    sub_ids = [x[constants.MID] for x in new_memories]
    exist = util.list_common(ids, sub_ids)
    total = total + len(exist)
    for nmem in new_memories:
        if total >= limit > 0:
            break
        if nmem[constants.MID] not in ids:
            convert_to_expectation(nmem)
            memories.append(nmem)
            total = total + 1


def associate(working_memories):
    # start = time.time()
    matched_memories = [mem for mem in working_memories if mem[constants.STATUS] is constants.MATCHED]
    logger.debug('len of matched_memories is {0}'.format(len(matched_memories)))
    related_memories = find_update_max_related_memories(matched_memories)
    logger.debug('len of related_memories is {0}'.format(len(related_memories)))
    append_working_memories(working_memories, related_memories)


def prepare_expectation(working_memories):
    # start = time.time()
    pending_memories = [mem for mem in working_memories if mem[constants.STATUS] is constants.MATCHING]
    logger.debug('len of pending_memories is {0}'.format(len(pending_memories)))
    for pmem in pending_memories:
        logger.debug('parent memory is {0}'.format(pmem))
        live_children = get_live_sub_memories(pmem, constants.CHILD_MEM)
        if pmem[constants.MEMORY_DURATION] is constants.INSTANT_MEMORY:
            logger.debug('constants.INSTANT_MEMORY live_children is {0}'.format(live_children))
            append_working_memories(working_memories, live_children)
        elif pmem[constants.MEMORY_DURATION] is constants.LONG_MEMORY or pmem[
            constants.MEMORY_DURATION] is constants.SHORT_MEMORY:
            logger.debug('live_children is {0}'.format(live_children))
            append_working_memories(working_memories, live_children, 1)
    # print 'prepare_expectation used time	' + str(time.time() - start)


def check_expectation(pending_memories, working_memories, sequential_time_memories):
    match_count = 0
    for pmem in pending_memories:
        if time.time() > pmem[constants.END_TIME]:
            pmem[constants.STATUS] = constants.EXPIRED
            continue
        all_matched = True
        child_ids = pmem[constants.CHILD_MEM]
        for wmem in working_memories:
            if wmem[constants.MID] in child_ids:
                if wmem[constants.STATUS] is not constants.MATCHED:
                    all_matched = False
                    break
        if all_matched:
            match_count = match_count + 1
            recall_memory(pmem)
            sequential_time_memories[pmem[constants.MEMORY_DURATION]].append(pmem)
    return match_count


def check_expectations(working_memories, sequential_time_memories):
    # start = time.time()
    error_memories = [mem for mem in working_memories if constants.STATUS not in mem]
    if len(error_memories) > 0:
        logger.error('error_memories is {0}'.format(error_memories))
    pending_instant_memories = [mem for mem in working_memories if
                                mem[constants.STATUS] is constants.MATCHING and
                                constants.MEMORY_DURATION in mem and
                                mem[constants.MEMORY_DURATION] is constants.INSTANT_MEMORY]
    check_expectation(pending_instant_memories, working_memories, sequential_time_memories)

    pending_short_memories = [mem for mem in working_memories if
                              mem[constants.STATUS] is constants.MATCHING and
                              constants.MEMORY_DURATION in mem and
                              mem[constants.MEMORY_DURATION] is constants.SHORT_MEMORY]
    check_expectation(pending_short_memories, working_memories, sequential_time_memories)

    pending_long_memories = [mem for mem in working_memories if
                             mem[constants.STATUS] is constants.MATCHING and
                             constants.MEMORY_DURATION in mem and
                             mem[constants.MEMORY_DURATION] is constants.LONG_MEMORY]
    match_count = check_expectation(pending_long_memories, working_memories, sequential_time_memories)

    while match_count > 0:
        # something change on long memory, try to match high level parent long memory
        pending_long_memories = [mem for mem in working_memories if
                                 mem[constants.STATUS] is constants.MATCHING and
                                 mem[constants.MEMORY_DURATION] is constants.LONG_MEMORY]
        match_count = check_expectation(pending_long_memories, working_memories, sequential_time_memories)
    # print 'check_expectation used time	' + str(time.time() - start)


def cleanup_working_memories(working_memories):
    # start = time.time()
    error_memories1 = [mem for mem in working_memories if constants.STATUS not in mem]
    if len(error_memories1) > 0:
        logger.error('error_memories1 is {0}'.format(error_memories1))
    error_memories2 = [mem for mem in working_memories if constants.END_TIME not in mem]
    if len(error_memories2) > 0:
        logger.error('error_memories is {0}'.format(error_memories2))
    valid_working_memories = [mem for mem in working_memories if
                              mem[constants.STATUS] is constants.MATCHED or mem[constants.END_TIME] > time.time()]
    sorted_working_memories = sorted(valid_working_memories, key=lambda x: (x[constants.LAST_ACTIVE_TIME]),
                                     reverse=True)
    limited_sorted_working_memories = sorted_working_memories[0:threshold_of_working_memories:]
    # print 'frame used time	' + str(time.time() - start)
    for mem in limited_sorted_working_memories:
        # as they survive, update last active time
        mem.update({constants.LAST_ACTIVE_TIME: time.time()})
    return limited_sorted_working_memories


def add_vision_feature_memory(feature_type, channel, kernel, feature):
    if isinstance(feature, np.ndarray):
        feature = feature.tolist()
    new_mem = add_physical_memory(
        {constants.PHYSICAL_MEMORY_TYPE: feature_type, constants.CHANNEL: channel, constants.KERNEL: kernel,
         constants.FEATURE: feature, constants.MEMORY_DURATION: constants.FEATURE_MEMORY})
    return new_mem


def add_feature_memory(feature_type, kernel, feature):
    if isinstance(feature, np.ndarray):
        feature = feature.tolist()
    new_mem = add_physical_memory(
        {constants.PHYSICAL_MEMORY_TYPE: feature_type, constants.KERNEL: kernel, constants.FEATURE: feature,
         constants.MEMORY_DURATION: constants.FEATURE_MEMORY})
    return new_mem


def add_collection_memory(mem_duration, child_memories, physical_memory_type='none', reward=0):
    child_memory_ids = [x[constants.MID] for x in child_memories]
    old_mem = data_adaptor.get_child_memory(child_memory_ids)
    if old_mem is None:
        memory_content = {constants.CHILD_MEM: child_memory_ids, constants.MEMORY_DURATION: mem_duration,
                          constants.REWARD: reward}
        if physical_memory_type is not 'none':
            memory_content.update({constants.PHYSICAL_MEMORY_TYPE: physical_memory_type})
        new_mem = add_memory(memory_content)
        increase_list_field(child_memories, constants.PARENT_MEM, new_mem[constants.MID])
    else:
        recall_memory(old_mem, {constants.REWARD: reward})
        new_mem = old_mem
    return new_mem


# please make sure it's not duplicated before calling it
def add_physical_memory(content):
    return add_memory(content)


def add_memory(content):
    mem = data_adaptor.add_memory(content)
    # below are used for working memory
    mem.update({constants.HAPPEN_TIME: time.time()})
    mem.update({constants.LAST_ACTIVE_TIME: time.time()})
    mem.update({constants.STATUS: constants.MATCHED})
    return mem


def activate_parent_memories(slice_memory, working_memories):
    working_memories_ids = [x[constants.MID] for x in working_memories]
    parent_working_memory_ids = util.list_common(slice_memory[constants.PARENT_MEM], working_memories_ids)
    while len(parent_working_memory_ids) > 0:
        grand_parent_memory_ids = []
        for memory_id in parent_working_memory_ids:
            for mem in working_memories:
                if mem[constants.MID] is memory_id:
                    mem.update({constants.LAST_ACTIVE_TIME: time.time()})
                    grand_parent_memory_ids.append(mem[constants.PARENT_MEM])
        parent_working_memory_ids = grand_parent_memory_ids


def verify_slice_memory_match_result(slice_memories, slice_memory_children, working_memories, sequential_time_memories):
    all_matched_feature_memories = []
    ids = []
    for slice_memory in slice_memories:
        smm_all_matched = True
        live_children = slice_memory_children.get(slice_memory[constants.MID])
        for feature_memory in live_children:
            if feature_memory[constants.STATUS] is constants.MATCHED:
                if feature_memory[constants.MID] not in ids:
                    feature_memory.update({constants.HAPPEN_TIME: time.time()})
                    working_memories.append(feature_memory)
                    all_matched_feature_memories.append(feature_memory)
                    ids.append(feature_memory[constants.MID])
            else:
                smm_all_matched = False
        if smm_all_matched:
            recall_memory(slice_memory)
            activate_parent_memories(slice_memory, working_memories)
            sequential_time_memories[constants.SLICE_MEMORY].append(slice_memory)
            working_memories.append(slice_memory)
    return all_matched_feature_memories


def add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories):
    if new_slice_memory is not None:
        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
        working_memories.append(new_slice_memory)