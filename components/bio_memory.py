import constants
import copy
import logging
import numpy as np
import random
import time
import util

logger = logging.getLogger('BioMemory')
logger.setLevel(logging.INFO)


class BioMemoryException(Exception):
    pass


class BioMemory(object):
    INTERVALS = 'itv'
    NEW_MEMORIES = 'nmm'
    REST_OF_MEMORIES = 'rom'
    CHILD_DAT1 = 'cd1'
    COMPOSE_NUMBER = 4
    DURATION_SLICE = 0.15
    DURATION_INSTANT = 0.5
    DURATION_SHORT = 3
    DURATION_LONG = 360
    GREEDY_RATIO = 0.8
    NOT_FORGET_STEP = 10

    #                                                                                                                                                                                  collections
    #                                                                                                                                        long                                   long            ...       long
    #                                                                                 short                                               short       ...       short
    #                             instant                                          instant         ...         instant
    # slice1        slice2      slice3      slice4      slice5 (max5)
    # vision1.1   vision2   vision3     vision4     vision5
    # sound1      sound2
    # vision1.2

    BASIC_MEMORY = {constants.STRENGTH: 0, constants.RECALL_COUNT: 0, constants.REWARD: 0, constants.PROTECT_TIME: 0,
                    constants.LAST_RECALL_TIME: 0, constants.PARENT_MEM: [], constants.CHILD_MEM: []}

    BASIC_MEMORY_GROUP_ARR = {constants.SLICE_MEMORY: [], constants.SHORT_MEMORY: [], constants.INSTANT_MEMORY: [],
                              constants.LONG_MEMORY: []}

    # The first recall time, if less than 60 seconds, memory strength is 100%, and then 99% for 61 seconds ... 21% for 35 days
    # TIME_SEC = [60, 61, 63, 66, 70, 75, 81, 88, 96, 105, 115, 126, 138, 151, 165, 180, 196, 213, 231, 250, 270, 291, 313, 336, 360, 385, 411, 438, 466, 495, 525, 540, 600, 660, 720,
    #             780, 840, 900, 960, 1020, 1080, 1140, 1200, 1260, 1320, 1440, 1560, 1740, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440, 14040, 18720,
    #             24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600, 537840, 853200, 1326240, 2035800, 3100140,
    #             3609835, 4203316, 4894372, 5699043, 6636009, 7727020, 8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033, 41225925,
    #             48003823, 55896067, 65085866]
    TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296,
                326, 358, 392, 428, 466, 506, 548, 593, 641, 692, 746, 803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367,
                1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440,
                14040, 18720, 24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600,
                537840, 853200, 1326240, 2035800, 3100140, 3609835, 4203316, 4894372, 5699043, 6636009, 7727020,
                8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033,
                41225925, 48003823, 55896067, 65085866]

    THRESHOLD_OF_WORKING_MEMORIES = 50

    def __init__(self, da):
        self.data_adaptor = da
        self.temp_memories = copy.deepcopy(self.BASIC_MEMORY_GROUP_ARR)
        self.working_memories = []
        self.matching_memories = []
        self.matching_child_memories = {}
        self.matched_memories = []

    def associate(self):
        # start = time.time()
        matched_memories = [mem for mem in self.working_memories if mem[constants.STATUS] is constants.MATCHED]
        logger.debug('len of matched_memories is {0}'.format(len(matched_memories)))
        related_memories = self.find_update_max_related_memories(matched_memories)
        logger.debug('len of related_memories is {0}'.format(len(related_memories)))
        self.new_working_memories(self.working_memories, related_memories)

    def prepare_matching_virtual_memories(self):
        start = time.time()
        pending_memories = [mem for mem in self.working_memories if mem[constants.STATUS] is constants.MATCHING]
        logger.debug('len of pending_memories is {0}'.format(len(pending_memories)))
        for bm in pending_memories:
            logger.debug('parent memory is {0}'.format(bm))
            if constants.VIRTUAL_MEMORY_TYPE in bm:
                if bm[constants.VIRTUAL_MEMORY_TYPE] is constants.INSTANT_MEMORY:
                    live_children = self.search_live_child_memories(bm)
                    logger.debug('constants.INSTANT_MEMORY live_children is {0}'.format(live_children))
                    self.new_working_memories(self.working_memories, live_children)
                elif bm[constants.VIRTUAL_MEMORY_TYPE] is constants.LONG_MEMORY or \
                        bm[constants.VIRTUAL_MEMORY_TYPE] is constants.SHORT_MEMORY:
                    live_children = self.search_live_child_memories(bm)
                    logger.debug('live_children is {0}'.format(live_children))
                    self.new_working_memories(self.working_memories, live_children, 1)
        logger.info('prepare_expectation used time	' + str(time.time() - start))

    def check_matching_virtual_memories(self):
        # start = time.time()
        instant_memories = [mem for mem in self.working_memories if
                            mem[constants.STATUS] is constants.MATCHING and
                            constants.VIRTUAL_MEMORY_TYPE in mem and
                            mem[constants.VIRTUAL_MEMORY_TYPE] is constants.INSTANT_MEMORY]
        self.check_matching_virtual_memory(instant_memories)

        short_memories = [mem for mem in self.working_memories if
                          mem[constants.STATUS] is constants.MATCHING and
                          constants.VIRTUAL_MEMORY_TYPE in mem and
                          mem[constants.VIRTUAL_MEMORY_TYPE] is constants.SHORT_MEMORY]
        self.check_matching_virtual_memory(short_memories)

        long_memories = [mem for mem in self.working_memories if
                         mem[constants.STATUS] is constants.MATCHING and
                         constants.VIRTUAL_MEMORY_TYPE in mem and
                         mem[constants.VIRTUAL_MEMORY_TYPE] is constants.LONG_MEMORY]
        match_count = self.check_matching_virtual_memory(long_memories, )

        while match_count > 0:
            # something change on long memory, try to match high level parent long memory
            long_memories = [mem for mem in self.working_memories if
                             mem[constants.STATUS] is constants.MATCHING and
                             mem[constants.VIRTUAL_MEMORY_TYPE] is constants.LONG_MEMORY]
            match_count = self.check_matching_virtual_memory(long_memories)
        # print 'check_expectation used time	' + str(time.time() - start)

    # slice memories of 4 (COMPOSE_NUMBER) or within DURATION_INSTANT will be grouped as a new instant memory
    # instant memories of 4 (COMPOSE_NUMBER) or within DURATION_SHORT will be grouped as a new short memory
    # short memories of 4 (COMPOSE_NUMBER) or within DURATION_LONG will be grouped as a new long memory
    def compose(self):
        start = time.time()
        result1 = self.split_seq_time_memories(self.temp_memories[constants.SLICE_MEMORY],
                                               self.DURATION_INSTANT)
        self.temp_memories[constants.SLICE_MEMORY] = result1[self.REST_OF_MEMORIES]
        self.add_collection_memories(result1[self.NEW_MEMORIES], constants.INSTANT_MEMORY)

        result2 = self.split_seq_time_memories(self.temp_memories[constants.INSTANT_MEMORY],
                                               self.DURATION_SHORT)
        self.temp_memories[constants.INSTANT_MEMORY] = result2[self.REST_OF_MEMORIES]
        self.add_collection_memories(result2[self.NEW_MEMORIES], constants.SHORT_MEMORY)

        result3 = self.split_seq_time_memories(self.temp_memories[constants.SHORT_MEMORY],
                                               self.DURATION_LONG)
        self.temp_memories[constants.SHORT_MEMORY] = result3[self.REST_OF_MEMORIES]
        self.add_collection_memories(result3[self.NEW_MEMORIES], constants.LONG_MEMORY)

        result4 = self.split_seq_time_memories(self.temp_memories[constants.LONG_MEMORY])
        self.temp_memories[constants.LONG_MEMORY] = result4[self.REST_OF_MEMORIES]
        self.add_collection_memories(result4[self.NEW_MEMORIES], constants.LONG_MEMORY)
        logger.info('compose used time	' + str(time.time() - start))

    def calculate_working_reward(self, memories):
        for bm in memories:
            reward = bm[constants.REWARD]
            elapse = int(time.time() - bm[constants.LAST_ACTIVE_TIME])
            ratio = 0
            # can't always keep in working memory, reduce it's working reward gradually
            if (100 - elapse) > 0:
                ratio = 100 - elapse
            # greedy mode, if satisfied (matched), will forget it soon, try to find another reward
            if bm[constants.STATUS] is constants.MATCHED:
                ratio = ratio * self.GREEDY_RATIO
            elif bm[constants.STATUS] is constants.EXPIRED:
                ratio = 0
            working_reward = reward * ratio
            bm.update({constants.WORKING_REWARD: working_reward})

    def cleanup_working_memories(self):
        # start = time.time()
        valid_working_memories = [mem for mem in self.working_memories if
                                  mem[constants.STATUS] is constants.MATCHED or mem[constants.END_TIME] > time.time()]
        self.calculate_working_reward(valid_working_memories)
        sorted_working_memories = sorted(valid_working_memories,
                                         key=lambda x: (x[constants.WORKING_REWARD], x[constants.LAST_ACTIVE_TIME]),
                                         reverse=True)
        limited_sorted_working_memories = sorted_working_memories[0:self.THRESHOLD_OF_WORKING_MEMORIES:]
        # print 'frame used time	' + str(time.time() - start)
        for mem in limited_sorted_working_memories:
            # as they survive, update last active time
            mem.update({constants.LAST_ACTIVE_TIME: time.time()})
        self.working_memories = limited_sorted_working_memories

    # longer time elapsed, easier to forget
    # more times recall, harder to forget
    # can not recall frequently in short time
    # check result, if memory.strength = -1, that it's forgot
    def refresh(self, mem, recall=False, is_forget=False):
        is_deleted = False
        now_time = int(time.time())
        time_elapse = now_time - mem[constants.LAST_RECALL_TIME]
        if time_elapse < self.TIME_SEC[0]:
            return is_deleted
        count = 0
        recall_count = mem[constants.RECALL_COUNT]
        for num in range(recall_count, len(self.TIME_SEC)):
            if self.TIME_SEC[num] <= time_elapse:
                count = count + 1
            else:
                strength = 100 - count
                mem[constants.STRENGTH] = strength
                # if go to next section
                if count > 0:
                    # random forget memory base on strength
                    if is_forget and time.time() > mem[constants.PROTECT_TIME]:
                        mem[constants.PROTECT_TIME] = self.calculate_protect_time(recall_count)
                        ran = random.randint(1, 100)
                        if ran > strength:
                            mem[constants.STRENGTH] = -1
                            is_deleted = True
                            break
                    # if this is recall, will update recall count and last recall time
                    if recall:
                        # mem[constants.STRENGTH] = 100
                        mem[constants.RECALL_COUNT] = recall_count + 1
                        mem[constants.LAST_RECALL_TIME] = int(time.time())
                break
        return is_deleted

    # add protect time to prevent frequent calculation of deletion
    def calculate_protect_time(self, recall_count):
        time_seq = np.array(self.TIME_SEC)
        end_number = recall_count + self.NOT_FORGET_STEP
        if end_number > len(time_seq):
            end_number = len(time_seq)
        sub_arr = time_seq[recall_count:end_number]
        return time.time() + np.sum(sub_arr)

    # summarize all parent memories in a list
    def count_parent_id(self, memories):
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

    def find_max_related_memories(self, memories, tobe_remove_list_ids, limit=4):
        # start = time.time()
        related_memories = []
        parent_counts = self.count_parent_id(memories)
        count = 0
        for key in sorted(parent_counts, key=parent_counts.get, reverse=True):
            mem = self.data_adaptor.get_memory(key)
            if mem:
                related_memories.append(mem)
                count = count + 1
            else:
                tobe_remove_list_ids.append(key)
            if count >= limit:
                break
        # print 'find_max_related_memories used time	' + str(time.time() - start)
        return related_memories

    def find_update_max_related_memories(self, memories, limit=4):
        # start = time.time()
        tobe_remove_list_ids = []
        related_memories = self.find_max_related_memories(memories, tobe_remove_list_ids, limit)
        if len(tobe_remove_list_ids) > 0:
            for mem in memories:
                self.reduce_list_field(constants.PARENT_MEM, mem[constants.PARENT_MEM], tobe_remove_list_ids,
                                       mem[constants.MID])
        # print 'find_update_max_related_memories used time	' + str(time.time() - start)
        return related_memories

    def increase_list_field(self, memories, field, new_id):
        logger.debug('increase_list_field')
        for mem in memories:
            ids = mem[field]
            if new_id not in ids:
                ids = util.np_array_concat(ids, [new_id])
                self.data_adaptor.update_memory({field: ids.tolist()}, mem[constants.MID])

    def reduce_list_field(self, field, sub_ids, forgot_ids, mid):
        new_sub = util.list_comprehension_new(sub_ids, forgot_ids)
        if field == constants.CHILD_MEM and len(new_sub) == 0:
            self.data_adaptor.remove_memory(mid)
        else:
            self.data_adaptor.update_memory({field: new_sub}, mid)

    def recall_feature_memory(self, mem, feature):
        if isinstance(feature, np.ndarray):
            feature = feature.tolist()
        update_content = {constants.FEATURE: feature}
        self.recall_memory(mem, update_content)

    def recall_memory(self, bm, addition=None):
        logger.debug('recall_memory')
        self.refresh(bm, True, False)
        update_content = {constants.STRENGTH: bm[constants.STRENGTH],
                          constants.RECALL_COUNT: bm[constants.RECALL_COUNT],
                          constants.LAST_RECALL_TIME: bm[constants.LAST_RECALL_TIME]}
        if addition is not None:
            update_content.update(addition)
            self.data_adaptor.update_memory(update_content, bm[constants.MID])
        bm.update(update_content)
        self.finish_working_memory(bm)

    def recall_virtual_memory(self, bm):
        if constants.VIRTUAL_MEMORY_TYPE not in bm:
            raise BioMemoryException('{0} is not a virtual memory'.format(bm))
        self.recall_memory(bm)
        self.temp_memories[bm[constants.VIRTUAL_MEMORY_TYPE]].append(bm)

    def recall_physical_memory(self, bm):
        self.recall_memory(bm)

    def remove_duplicate_memory(self, memories):
        logger.debug('remove_duplicate_memory')
        new_memories = []
        new_memories_ids = []
        for mem in memories:
            if mem[constants.MID] not in new_memories_ids:
                new_memories.append(mem)
                new_memories_ids.append(mem[constants.MID])
        return new_memories

    # split memory array to certain groups by number or elapse time
    # new memories can be found in NEW_MEMORIES of result
    # distance of each child memory can be found in CHILD_DAT1 of result
    # rest of memories that are not composed can be found in REST_OF_MEMORIES of result
    def split_seq_time_memories(self, memories, gap=60.0):
        count = 0
        last_time = 0
        elapse_time = 0
        groups = []
        group = []
        add_datas = []
        add_data = []
        for mem in memories:
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
            if count >= self.COMPOSE_NUMBER:
                groups.append(group)
                group = []
                count = 0
                elapse_time = 0
        result = {
            self.NEW_MEMORIES: groups,
            self.CHILD_DAT1: add_datas,
            self.REST_OF_MEMORIES: group
        }
        return result

    def finish_working_memory(self, bm):
        logger.debug('finish_working_memory')
        bm.update({constants.HAPPEN_TIME: time.time()})
        bm.update({constants.LAST_ACTIVE_TIME: time.time()})
        bm.update({constants.STATUS: constants.MATCHED})
        ids = [bm[constants.MID] for bm in self.working_memories]
        if bm[constants.MID] not in ids:
            self.working_memories.append(bm)

    def new_working_memory(self, bm):
        exp = {constants.STATUS: constants.MATCHING, constants.START_TIME: time.time(),
               constants.LAST_ACTIVE_TIME: time.time()}
        if bm[constants.VIRTUAL_MEMORY_TYPE] is constants.INSTANT_MEMORY:
            exp.update({constants.END_TIME: time.time() + self.DURATION_INSTANT})
        elif bm[constants.VIRTUAL_MEMORY_TYPE] is constants.SHORT_MEMORY:
            exp.update({constants.END_TIME: time.time() + self.DURATION_SHORT})
        elif bm[constants.VIRTUAL_MEMORY_TYPE] is constants.LONG_MEMORY:
            exp.update({constants.END_TIME: time.time() + self.DURATION_LONG})
        elif bm[constants.VIRTUAL_MEMORY_TYPE] is constants.SLICE_MEMORY:
            exp.update({constants.END_TIME: time.time() + self.DURATION_SLICE})
        bm.update(exp)

    # append new memories to memories list if it's not exist
    def new_working_memories(self, memories, new_memories, limit=0):
        total = 0
        ids = [x[constants.MID] for x in memories]
        sub_ids = [x[constants.MID] for x in new_memories]
        exist = util.list_common(ids, sub_ids)
        total = total + len(exist)
        for nmem in new_memories:
            if total >= limit > 0:
                break
            if nmem[constants.MID] not in ids:
                self.new_working_memory(nmem)
                memories.append(nmem)
                total = total + 1

    def update_last_recall(self, memories):
        for mem in memories:
            self.data_adaptor.update_memory({constants.LAST_RECALL_TIME: int(time.time())}, mem[constants.MID])

    def check_matching_virtual_memory(self, pending_memories):
        match_count = 0
        for pbm in pending_memories:
            if time.time() > pbm[constants.END_TIME]:
                pbm[constants.STATUS] = constants.EXPIRED
                continue
            all_matched = True
            child_ids = pbm[constants.CHILD_MEM]
            for wbm in self.working_memories:
                if wbm[constants.MID] in child_ids:
                    if wbm[constants.STATUS] is not constants.MATCHED:
                        all_matched = False
                        break
            if all_matched:
                match_count = match_count + 1
                self.recall_virtual_memory(pbm)
                logger.info('reproduce virtual memories {0}'.format(pbm))
        return match_count

    def activate_parent_memories(self, bm):
        memories_ids = [x[constants.MID] for x in self.working_memories]
        parent_working_memory_ids = util.list_common(bm[constants.PARENT_MEM], memories_ids)
        while len(parent_working_memory_ids) > 0:
            grand_parent_memory_ids = []
            for memory_id in parent_working_memory_ids:
                for mem in self.working_memories:
                    if mem[constants.MID] is memory_id:
                        mem.update({constants.LAST_ACTIVE_TIME: time.time()})
                        grand_parent_memory_ids.append(mem[constants.PARENT_MEM])
            parent_working_memory_ids = grand_parent_memory_ids

    def add_memory(self, content):
        start = time.time()
        logger.debug('add_memory start')
        bm = self.data_adaptor.add_memory(content)
        logger.debug('adding memory used {0}'.format(time.time() - start))
        self.finish_working_memory(bm)
        # below are used for working memory
        return bm

    # please make sure it's not duplicated before calling it
    def add_physical_memory(self, content):
        if constants.PHYSICAL_MEMORY_TYPE not in content:
            raise BioMemoryException('not a physical memory')
        return self.add_memory(content)

    def add_feature_memory(self, feature_type, kernel, feature, addition=None):
        if isinstance(feature, np.ndarray):
            feature = feature.tolist()
        content = {constants.PHYSICAL_MEMORY_TYPE: feature_type, constants.KERNEL: kernel, constants.FEATURE: feature}
        if addition:
            content.update(addition)
        new_mem = self.add_physical_memory(content)
        return new_mem

    def add_vision_feature_memory(self, feature_type, channel, kernel, feature):
        addition = {constants.CHANNEL: channel}
        return self.add_feature_memory(feature_type, kernel, feature, addition)

    def add_mouse_click_memory(self, click_type):
        content = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_MOUSE_CLICK, constants.CLICK_TYPE: click_type}
        return self.add_physical_memory(content)

    def add_reward_memory(self, reward):
        content = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_REWARD, constants.REWARD: reward}
        return self.add_physical_memory(content)

    def add_vision_focus_move_memory(self, degrees, speed, duration):
        content = {constants.DEGREES: degrees, constants.SPEED: speed, constants.MOVE_DURATION: duration,
                   constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE}
        return self.add_physical_memory(content)

    def add_vision_focus_zoom_memory(self, zoom_type, zoom_direction):
        content = {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_ZOOM, constants.ZOOM_TYPE: zoom_type,
                   constants.ZOOM_DIRECTION: zoom_direction}
        return self.add_physical_memory(content)

    def add_virtual_memory(self, bm_type, child_memories, addition=None, reward=0):
        logger.debug('add_virtual_memory')
        memories = self.remove_duplicate_memory(child_memories)
        memory_ids = [x[constants.MID] for x in memories]
        existing_bm = self.data_adaptor.get_by_child_ids(memory_ids)
        if existing_bm is None:
            memory_content = {constants.CHILD_MEM: memory_ids, constants.VIRTUAL_MEMORY_TYPE: bm_type,
                              constants.REWARD: reward}
            if addition:
                memory_content.update(addition)
            bm = self.add_memory(memory_content)
            self.increase_list_field(memories, constants.PARENT_MEM, bm[constants.MID])
        else:
            self.recall_memory(existing_bm, {constants.REWARD: reward})
            bm = existing_bm
        self.temp_memories[bm_type].append(bm)
        return bm

    # children is list of group memories [[m1, m2], [m3, m4]]
    def add_collection_memories(self, memory_groups, duration_type):
        if memory_groups is None or len(memory_groups) == 0:
            return
        for child_memories in memory_groups:
            if len(child_memories) > 0:
                child_memory_rewards = [mem[constants.REWARD] for mem in child_memories]
                max_reward = np.max(np.array(child_memory_rewards))
                # new_reward is int32, which will become "\x00\x00\x00\x00" when insert to CodernityDB
                max_reward = int(max_reward)
                new_reward = max_reward - 1
                if new_reward < 0:
                    new_reward = 0
                self.add_virtual_memory(duration_type, child_memories, reward=new_reward)

    def add_slice_memory(self, memories, bm_type):
        logger.debug('add_slice_memoryv')
        ids = [x[constants.MID] for x in memories]
        sbm = self.data_adaptor.get_by_child_ids(ids)
        if sbm is None:
            addition = {constants.PHYSICAL_MEMORY_TYPE: bm_type}
            self.add_virtual_memory(constants.SLICE_MEMORY, memories, addition)
        else:
            self.recall_virtual_memory(sbm)

    def prepare_matching_physical_memories(self, bm_type):
        self.matching_memories = []
        self.matching_child_memories = {}
        physical_memories = []
        child_memories = {}
        slice_memories = self.get_working_memories(bm_type)
        for bm in slice_memories:
            live_children = self.search_live_child_memories(bm, physical_memories)
            child_memories.update({bm[constants.MID]: live_children})
        self.matching_memories = slice_memories
        self.matching_child_memories = child_memories
        return physical_memories

    def verify_matching_physical_memories(self):
        self.matched_memories = []
        physical_memories = []
        ids = []
        for sbm in self.matching_memories:
            sbm_all_matched = True
            live_children = self.matching_child_memories.get(sbm[constants.MID])
            for feature_memory in live_children:
                if feature_memory[constants.STATUS] is constants.MATCHED:
                    if feature_memory[constants.MID] not in ids:
                        physical_memories.append(feature_memory)
                        ids.append(feature_memory[constants.MID])
                else:
                    sbm_all_matched = False
            if sbm_all_matched:
                self.recall_virtual_memory(sbm)
                self.activate_parent_memories(sbm)
        self.matched_memories = physical_memories
        if len(physical_memories) > 0:
            logger.debug('reproduce physical memories {0}'.format(physical_memories))

    def enrich_feature_memories(self, bm_type, fbm):
        logger.debug('enrich_feature_memories')
        matched_ids = [x[constants.MID] for x in self.matched_memories]
        if fbm is not None and fbm[constants.MID] not in matched_ids:
            self.matched_memories.append(fbm)
        if len(self.matched_memories) > 0:
            self.add_slice_memory(self.matched_memories, bm_type)

    def get_working_memories(self, bm_type):
        return [bm for bm in self.working_memories if constants.VIRTUAL_MEMORY_TYPE in bm and
                bm[constants.VIRTUAL_MEMORY_TYPE] is constants.SLICE_MEMORY and
                bm[constants.STATUS] is constants.MATCHING and
                constants.PHYSICAL_MEMORY_TYPE in bm and bm[constants.PHYSICAL_MEMORY_TYPE] is bm_type]

    def get_vision_move_memory(self, degrees, speed, duration):
        return self.data_adaptor.get_vision_move_memory(degrees, speed, duration)

    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        return self.data_adaptor.get_vision_zoom_memory(zoom_type, zoom_direction)

    def get_mouse_click_memory(self, click_type):
        return self.data_adaptor.get_mouse_click_memory(click_type)

    def search_live_memories(self, memory_ids):
        memories = []
        for mid in memory_ids:
            mem = self.data_adaptor.get_memory(mid)
            if mem is not None:
                memories.append(mem)
        return memories

    # bm should be a virtual memory, have children
    def search_live_child_memories(self, bm, all_child_bm=None, limit=0, offset=0):
        child_bm_ids = bm[constants.CHILD_MEM]
        forgot_ids = []
        child_bm = []
        count = 0
        total = limit
        if total == 0:
            total = len(child_bm_ids)
        for i in range(offset, total):
            sub_id = child_bm_ids[i]
            sub_bm = None
            if all_child_bm is not None:
                for ebm in all_child_bm:
                    if ebm[constants.MID] == sub_id:
                        # found in all_child_bm
                        sub_bm = ebm
                        child_bm.append(sub_bm)
                        break
            if sub_bm is None:
                sub_bm = self.data_adaptor.get_memory(sub_id)
                if sub_bm is not None:
                    sub_bm.update({constants.STATUS: constants.MATCHING})
                    child_bm.append(sub_bm)
                    if all_child_bm is not None:
                        all_child_bm.append(sub_bm)
                else:
                    forgot_ids.append(sub_id)
                    logger.debug('forgot something')
            count = count + 1
            if count >= total:
                break
        if len(forgot_ids) > 0:
            self.reduce_list_field(constants.CHILD_MEM, child_bm_ids, forgot_ids, bm[constants.MID])
        if len(child_bm) == 0:
            # virtual memory should have children
            self.data_adaptor.remove_memory(bm[constants.MID])
        return child_bm
