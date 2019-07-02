from .bio_memory import BioMemory
from . import constants
import logging
import os
import numpy as np
import time
from . import util
import uuid

logger = logging.getLogger('DataAdaptor')
logger.setLevel(logging.INFO)


class DataAdaptor:
    start_thread = True
    seq = 0

    def __init__(self, db):
        self.db = db
        bm = BioMemory(self)
        self.bio_memory = bm
        if not os.path.exists('data'):
            os.makedirs('data')

    # return None if not found
    # do not use directly, we usually need to refresh it before getting it
    def _get_memory(self, mid):
        start = time.time()
        record = self.db.get_by_id(mid)
        logger.debug('get record used {0}'.format(time.time() - start))
        return record

    # return None if not found
    def get_memory(self, mid, recall=False):
        mem = self._get_memory(mid)
        # do not clean memory in individual call, rely on gc
        # if mem is not None:
        #     self.bio_memory.refresh(mem, recall, True)
        #     if mem[constants.STRENGTH] == -1:
        #         self.remove_memory(mem[constants.MID])
        #         return None
        return mem

    def get_all_memories(self):
        return self.db.get_all()

    def update_memory(self, content, mid):
        return self.db.update_memory(content, mid)

    def update_memories(self, contents):
        logger.debug('update_memories')
        if len(contents) == 0:
            return
        self.db.update_memories(contents)

    def delete_memory(self, mid):
        start = time.time()
        self.db.delete_memory(mid)
        logger.debug('delete_memory used {0}'.format(time.time() - start))

    def delete_memories(self, mids):
        logger.debug('delete_memories')
        if not mids:
            return
        if len(mids) == 0:
            return
        start = time.time()
        self.db.delete_memories(mids)
        logger.debug('delete_memories used {0}'.format(time.time() - start))

    def search_invalid_memories(self, memories):
        start = time.time()
        if memories is None or len(memories) == 0:
            return None
        to_be_deleted_memories = []
        for mem in memories:
            self.bio_memory.refresh(mem, False, True)
            if mem[constants.STRENGTH] == -1:
                to_be_deleted_memories.append(mem[constants.MID])
        logger.debug('refresh_memories used {0}'.format(time.time() - start))
        return to_be_deleted_memories

    def search_invalid_fields(self, memories, field):
        start = time.time()
        to_be_update_memories = []
        for mem in memories:
            original_list = mem[field]
            # fine unique value from list
            distinct_list = [x for x in set(original_list)]
            new_list = []
            for element in distinct_list:
                sub_mem = self._get_memory(element)
                if sub_mem is not None:
                    new_list.append(element)
            if len(new_list) != len(original_list):
                to_be_update_memories.append({field: new_list, constants.MID: mem[constants.MID]})
        logger.debug('search_outdated_memory_by_field used {0}'.format(time.time() - start))
        return to_be_update_memories

    # private method
    def _add_record(self, content):
        uid = str(uuid.uuid4())
        uid = uid.replace('-', '')
        content.update(
            {constants.MID: uid, constants.STRENGTH: 100, constants.RECALL_COUNT: 1,
             constants.LAST_RECALL_TIME: int(time.time())})
        start = time.time()
        self.db.insert(content)
        logger.debug('insert record used {0}'.format(time.time() - start))
        return uid

    # it return new created record id, normally not use it
    def _add_memory(self, addition=None):
        new_memory = self.bio_memory.BASIC_MEMORY.copy()
        if addition is not None:
            new_memory.update(addition)
        return self._add_record(new_memory)

    def add_memory(self, addition=None):
        mid = self._add_memory(addition)
        result = self._get_memory(mid)
        return result

    def get_vision_move_memory(self, degrees, speed, duration):
        record = self.db.get_vision_move_memory(degrees, speed, duration)
        return record

    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        record = self.db.get_vision_zoom_memory(zoom_type, zoom_direction)
        return record

    def get_mouse_click_memory(self, click_type):
        record = self.db.get_mouse_click_memory(click_type)
        return record

    def get_vision_feature_memories(self, kernel, channel):
        record = self.db.get_vision_feature_memories(kernel, channel)
        return record

    def get_sound_feature_memories(self, kernel):
        record = self.db.get_sound_feature_memories(kernel)
        return record

    def get_top_vision_used_kernel(self, offset):
        record = self.db.get_top_vision_used_kernel(offset)
        return record

    def put_vision_used_kernel(self, kernel):
        record = self.db.get_vision_used_kernel(kernel)
        if record is None:
            self.db.insert_vision_used_kernel(kernel)
        else:
            self.db.update_vision_used_kernel(kernel, record[constants.COUNT] + 1)

    def get_top_sound_used_kernel(self, offset):
        record = self.db.get_top_sound_used_kernel(offset)
        return record

    def put_sound_used_kernel(self, kernel):
        record = self.db.get_sound_used_kernel(kernel)
        if record is None:
            self.db.insert_sound_used_kernel(kernel)
        else:
            self.db.update_sound_used_kernel(kernel, record[constants.COUNT] + 1)

    def get_top_used_speed(self, offset):
        record = self.db.get_top_used_speed(offset)
        return record

    def put_used_speed(self, speed):
        record = self.db.get_used_speed(speed)
        if record is None:
            self.db.insert_used_speed(speed)
        else:
            self.db.update_used_speed(speed, record[constants.COUNT] + 1)

    def get_top_used_degrees(self, offset):
        record = self.db.get_top_used_degrees(offset)
        return record

    def put_used_degrees(self, degrees):
        record = self.db.get_used_degrees(degrees)
        if record is None:
            self.db.insert_used_degrees(degrees)
        else:
            self.db.update_used_degrees(degrees, record[constants.COUNT] + 1)

    def get_top_used_channel(self, offset):
        record = self.db.get_top_used_channel(offset)
        return record

    def put_used_channel(self, channel):
        record = self.db.get_used_channel(channel)
        if record is None:
            self.db.insert_used_channel(channel)
        else:
            self.db.update_used_channel(channel, record[constants.COUNT] + 1)

    def get_by_child_ids(self, child_mem):
        record = self.db.get_by_child_ids(child_mem)
        return record

    def get_eden_memories(self):
        record = self.db.get_eden_memories()
        return record

    def get_young_memories(self):
        record = self.db.get_young_memories()
        return record

    def get_old_memories(self):
        record = self.db.get_old_memories()
        return record

    def get_memories_by_id_mod(self, mod):
        records = self.db.get_memories_by_id_mod(mod)
        return records

    def find_duplication(self, field):
        memories = self.get_all_memories()
        count = 0
        for i in range(0, len(memories) - 1):
            list1 = memories[i].get(field)
            for j in range(i + 1, len(memories)):
                list2 = memories[j].get(field)
                if len(list1) > 0 and util.list_equal(list1, list2):
                    count = count + 1
                    break
        return count

    def synchronize_memory_time(self, system_last_active_time):
        logger.info('start to synchronize memories')
        gap = time.time() - system_last_active_time
        records = self.db.get_all()
        to_update_memories = []
        for mem in records:
            last_recall_time = mem[constants.LAST_RECALL_TIME]
            to_update_memories.append(
                {constants.MID: mem[constants.MID], constants.LAST_RECALL_TIME: last_recall_time + gap})
        if len(to_update_memories) > 0:
            self.db.update_memories(to_update_memories)

    def clean_vision_used_kernel(self):
        self.db.clean_vision_used_kernel()

    def clean_sound_used_kernel(self):
        self.db.clean_sound_used_kernel()

    def clean_short_id(self):
        self.db.clean_short_id()

    def persist(self):
        self.db.persist()

    def display_bm_tree_leaf(self, mid, level=0, max_level=2):
        if level >= max_level:
            print('hit max level, return')
            return
        bm = self.get_memory(mid)
        level_line = ''
        for i in range(0, level):
            level_line = '---{0}'.format(level_line)
        if bm is None:
            print('None')
        else:
            leaf_debug = 'l{0}:{1} id:{2},sid:{3},vmt:{4},pmt:{5},count:{6}'. \
                format(level, level_line, mid, bm.get(constants.ID), bm.get(constants.VIRTUAL_MEMORY_TYPE),
                       bm.get(constants.PHYSICAL_MEMORY_TYPE), bm.get(constants.RECALL_COUNT))
            print(leaf_debug)
            logger.info(leaf_debug)
            cms = bm[constants.CHILD_MEM]
            clevel = level + 1
            for cmid in cms:
                self.display_bm_tree_leaf(cmid, clevel, max_level)

    def find_bm_tree_roots(self, mid, roots):
        bm = self.get_memory(mid)
        if bm is not None:
            pms = bm[constants.PARENT_MEM]
            if bm[constants.VIRTUAL_MEMORY_TYPE] == constants.LONG_MEMORY or \
                    bm[constants.VIRTUAL_MEMORY_TYPE] == constants.SHORT_MEMORY:
                if bm[constants.MID] not in roots:
                    roots.append(bm[constants.MID])
            for pmid in pms:
                self.find_bm_tree_roots(pmid, roots)
