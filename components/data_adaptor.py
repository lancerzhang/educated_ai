from .bio_memory import BioMemory
from . import constants
import logging
import os
import time
from . import util
import uuid

logger = logging.getLogger('DataAdaptor')
logger.setLevel(logging.ERROR)


class DataAdaptor:
    start_thread = True
    seq = 0

    @util.timeit
    def __init__(self, db):
        self.db = db
        bm = BioMemory(self)
        self.bio_memory = bm
        if not os.path.exists('data'):
            os.makedirs('data')

    # return None if not found
    # do not use directly, we usually need to refresh it before getting it
    @util.timeit
    def _get_memory(self, mid):
        record = self.db.get_by_id(mid)
        return record

    # return None if not found
    @util.timeit
    def get_memory(self, mid):
        mem = self._get_memory(mid)
        return mem

    @util.timeit
    def get_all_memories(self):
        records = self.db.get_all()
        return records

    @util.timeit
    def update_memory(self, content, mid):
        return self.db.update_memory(content, mid)

    @util.timeit
    def update_memories(self, contents):
        if len(contents) == 0:
            return
        self.db.update_memories(contents)

    @util.timeit
    def delete_memory(self, mid):
        self.db.delete_memory(mid)

    @util.timeit
    def delete_memories(self, mids):
        if not mids:
            return
        if len(mids) == 0:
            return
        self.db.delete_memories(mids)

    @util.timeit
    def search_invalid_memories(self, memories):
        if memories is None or len(memories) == 0:
            return None
        to_be_deleted_memories = []
        for mem in memories:
            self.bio_memory.refresh(mem, False, True)
            if mem[constants.STRENGTH] == -1:
                to_be_deleted_memories.append(mem[constants.MID])
        return to_be_deleted_memories

    @util.timeit
    def search_invalid_fields(self, memories, field):
        to_be_update_memories = []
        all_memories = self.db.get_all()
        all_ids = [x[constants.MID] for x in all_memories]
        for mem in memories:
            original_list = mem[field]
            new_list = util.list_common(original_list, all_ids)
            if len(new_list) != len(original_list):
                to_be_update_memories.append({field: new_list, constants.MID: mem[constants.MID]})
        return to_be_update_memories

    # private method
    @util.timeit
    def _add_record(self, content):
        uid = str(uuid.uuid4())
        uid = uid.replace('-', '')
        content.update(
            {constants.MID: uid, constants.STRENGTH: 100, constants.RECALL_COUNT: 1,
             constants.LAST_RECALL_TIME: int(time.time())})
        record = self.db.get_insert(content)
        return record

    # it return new created record id, normally not use it
    @util.timeit
    def _add_memory(self, addition=None):
        new_memory = self.bio_memory.BASIC_MEMORY.copy()
        if addition is not None:
            new_memory.update(addition)
        return self._add_record(new_memory)

    @util.timeit
    def add_memory(self, addition=None):
        return self._add_memory(addition)

    @util.timeit
    def get_vision_move_memory(self, degrees, speed, duration):
        record = self.db.get_vision_move_memory(degrees, speed, duration)
        return record

    @util.timeit
    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        record = self.db.get_vision_zoom_memory(zoom_type, zoom_direction)
        return record

    @util.timeit
    def get_mouse_click_memory(self, click_type):
        record = self.db.get_mouse_click_memory(click_type)
        return record

    @util.timeit
    def get_vision_feature_memories(self, kernel, channel):
        record = self.db.get_vision_feature_memories(kernel, channel)
        return record

    @util.timeit
    def get_sound_feature_memories(self, kernel):
        record = self.db.get_sound_feature_memories(kernel)
        return record

    @util.timeit
    def get_top_vision_used_kernel(self, offset):
        record = self.db.get_top_vision_used_kernel(offset)
        return record

    @util.timeit
    def put_vision_used_kernel(self, kernel):
        record = self.db.get_vision_used_kernel(kernel)
        if record is None:
            self.db.insert_vision_used_kernel(kernel)
        else:
            self.db.update_vision_used_kernel(kernel, record[constants.COUNT] + 1)

    @util.timeit
    def get_top_sound_used_kernel(self, offset):
        record = self.db.get_top_sound_used_kernel(offset)
        return record

    @util.timeit
    def put_sound_used_kernel(self, kernel):
        record = self.db.get_sound_used_kernel(kernel)
        if record is None:
            self.db.insert_sound_used_kernel(kernel)
        else:
            self.db.update_sound_used_kernel(kernel, record[constants.COUNT] + 1)

    @util.timeit
    def get_top_used_speed(self, offset):
        record = self.db.get_top_used_speed(offset)
        return record

    @util.timeit
    def put_used_speed(self, speed):
        record = self.db.get_used_speed(speed)
        if record is None:
            self.db.insert_used_speed(speed)
        else:
            self.db.update_used_speed(speed, record[constants.COUNT] + 1)

    @util.timeit
    def get_top_used_degrees(self, offset):
        record = self.db.get_top_used_degrees(offset)
        return record

    @util.timeit
    def put_used_degrees(self, degrees):
        record = self.db.get_used_degrees(degrees)
        if record is None:
            self.db.insert_used_degrees(degrees)
        else:
            self.db.update_used_degrees(degrees, record[constants.COUNT] + 1)

    @util.timeit
    def get_top_used_channel(self, offset):
        record = self.db.get_top_used_channel(offset)
        return record

    @util.timeit
    def put_used_channel(self, channel):
        record = self.db.get_used_channel(channel)
        if record is None:
            self.db.insert_used_channel(channel)
        else:
            self.db.update_used_channel(channel, record[constants.COUNT] + 1)

    @util.timeit
    def get_by_child_ids(self, child_mem):
        record = self.db.get_by_child_ids(child_mem)
        return record

    @util.timeit
    def get_eden_memories(self):
        record = self.db.get_eden_memories()
        return record

    @util.timeit
    def get_young_memories(self):
        record = self.db.get_young_memories()
        return record

    @util.timeit
    def get_old_memories(self):
        record = self.db.get_old_memories()
        return record

    @util.timeit
    def get_memories_by_id_mod(self, mod):
        records = self.db.get_memories_by_id_mod(mod)
        return records

    @util.timeit
    def synchronize_memory_time(self, system_last_active_time):
        gap = time.time() - system_last_active_time
        records = self.db.get_all()
        to_update_memories = []
        for mem in records:
            last_recall_time = mem[constants.LAST_RECALL_TIME]
            to_update_memories.append(
                {constants.MID: mem[constants.MID], constants.LAST_RECALL_TIME: last_recall_time + gap})
        if len(to_update_memories) > 0:
            self.db.update_memories(to_update_memories)

    @util.timeit
    def clean_vision_used_kernel(self):
        self.db.clean_vision_used_kernel()

    @util.timeit
    def clean_sound_used_kernel(self):
        self.db.clean_sound_used_kernel()

    @util.timeit
    def clean_short_id(self):
        self.db.clean_short_id()

    @util.timeit
    def persist(self):
        self.db.persist()

    @util.timeit
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

    @util.timeit
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
