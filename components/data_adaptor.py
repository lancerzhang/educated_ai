from bio_memory import BioMemory
import constants
import logging
import numpy as np
import time
import util
import uuid

logger = logging.getLogger('DataAdaptor')
logger.setLevel(logging.INFO)


class DataAdaptor:
    start_thread = True
    seq = 0
    SHORT_ID_FILE = 'data/sid.npy'

    def __init__(self, db):
        self.db = db
        bm = BioMemory(self)
        self.bio_memory = bm
        try:
            self.short_id_nd_list = np.load(self.SHORT_ID_FILE)
        except IOError:
            self.short_id_nd_list = np.array({})

    # return None if not found
    # do not use directly, we usually need to refresh it before getting it
    def _get_memory(self, mid):
        return self.db.get_by_id(mid)

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
        return self.db.update(content, mid)

    def remove_memory(self, mid):
        self.db.remove(mid)

    def refresh_memories(self, memories, recall=False):
        live_memories = []
        if memories is None or len(memories) == 0:
            return None
        for mem in memories:
            self.bio_memory.refresh(mem, recall, True)
            if mem[constants.STRENGTH] == -1:
                self.remove_memory(mem[constants.MID])
            else:
                live_memories.append(mem)
        return live_memories

    def cleanup_fields(self):
        self.cleanup_field(constants.PARENT_MEM, 'full')

    def cleanup_field(self, field, clean_type):
        start = time.time()
        logger.info('start to cleanup_fields {0} memory'.format(clean_type))
        if clean_type == constants.EDEN:
            records = self.db.get_eden_memories()
        elif clean_type == constants.YOUNG:
            records = self.db.get_young_memories()
        elif clean_type == constants.OLD:
            records = self.db.get_old_memories()
        else:
            records = self.db.get_all()
        for mem in records:
            original_list = mem[field]
            # fine unique value from list
            distinct_list = [x for x in set(original_list)]
            new_list = []
            for element in distinct_list:
                sub_mem = self._get_memory(element)
                if sub_mem is not None:
                    new_list.append(element)
            if len(new_list) != len(original_list):
                logger.debug('clean up from {0} to {1}'.format(len(original_list), len(new_list)))
                self.update_memory({field: new_list}, mem[constants.MID])
        logger.info('cleanup_fields used time {0}'.format(time.time() - start))

    # def schedule_housekeep(self):
    #     self.seq = self.seq + 1
    #     while self.start_thread:
    #         self.full_housekeep()
    #         time.sleep(30)

    def gc(self, gc_type):
        start = time.time()
        logger.info('start to gc {0} memory'.format(gc_type))
        if gc_type == constants.EDEN:
            records = self.db.get_eden_memories()
        elif gc_type == constants.YOUNG:
            records = self.db.get_young_memories()
        elif gc_type == constants.OLD:
            records = self.db.get_old_memories()
        else:
            records = self.db.get_all()
        logger.info('memories to be refresh:{0}'.format(len(records)))
        lives = self.refresh_memories(records)
        if records is None:
            cleaned = 0
        elif lives is None:
            cleaned = len(records)
        else:
            cleaned = len(records) - len(lives)
        logger.info('memories were deleted:{0}'.format(cleaned))
        logger.info('{0} gc used time {1}'.format(gc_type, time.time() - start))
        if gc_type == constants.YOUNG or gc_type == constants.OLD:
            self.cleanup_field(constants.PARENT_MEM, gc_type)
        return cleaned

    def full_gc(self):
        return self.gc('full')

    def partial_gc(self):
        self.seq = self.seq + 1
        start = time.time()
        logger.debug('start to partial housekeep memory')
        records = self.db.search_housekeep(self.seq % 100)
        logger.debug('memories to be refresh:{0}'.format(len(records)))
        lives = self.refresh_memories(records)
        if records is None:
            cleaned = 0
        elif lives is None:
            cleaned = len(records)
        else:
            cleaned = len(records) - len(lives)
        logger.debug('memories were deleted:{0}'.format(cleaned))
        logger.debug('partial_housekeep used time:{0}'.format(time.time() - start))
        return cleaned

    # private method
    def _add_record(self, content):
        uid = str(uuid.uuid4())
        uid = uid.replace('-', '')
        content.update(
            {constants.MID: uid, constants.STRENGTH: 100, constants.RECALL_COUNT: 1,
             constants.LAST_RECALL_TIME: int(time.time())})
        record = self.db.insert(content)
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
        for mem in records:
            last_recall_time = mem[constants.LAST_RECALL_TIME]
            self.update_memory({constants.LAST_RECALL_TIME: last_recall_time + gap}, mem[constants.MID])

    def keep_fit(self):
        self.db.keep_fit()

    def display_bm_tree_leaf(self, mid, level=0, max_level=2):
        if level >= max_level:
            print 'hit max level, return'
            return
        bm = self.get_memory(mid)
        level_line = ''
        for i in range(0, level):
            level_line = '---{0}'.format(level_line)
        if bm is None:
            print 'None'
        else:
            leaf_debug = 'l{0}:{1} id:{2},sid:{3},vmt:{4},pmt:{5},count:{6}'. \
                format(level, level_line, mid, self.get_short_id(mid), bm.get(constants.VIRTUAL_MEMORY_TYPE),
                       bm.get(constants.PHYSICAL_MEMORY_TYPE), bm.get(constants.RECALL_COUNT))
            print leaf_debug
            logger.info(leaf_debug)
            cms = bm[constants.CHILD_MEM]
            clevel = level + 1
            for cmid in cms:
                self.display_bm_tree_leaf(cmid, clevel, max_level)

    def find_bm_tree_roots(self, mid, roots):
        bm = self.get_memory(mid)
        if bm is not None:
            pms = bm[constants.PARENT_MEM]
            if bm[constants.VIRTUAL_MEMORY_TYPE] == constants.LONG_MEMORY or bm[constants.VIRTUAL_MEMORY_TYPE] == constants.SHORT_MEMORY:
                if bm[constants.MID] not in roots:
                    roots.append(bm[constants.MID])
            for pmid in pms:
                self.find_bm_tree_roots(pmid, roots)

    def get_short_id(self, long_id):
        short_id_list = self.short_id_nd_list.tolist()
        short_id = short_id_list.get(long_id)
        if short_id is None:
            short_id = len(short_id_list) + 1
            short_id_list.update({long_id: short_id})
            np.save(self.SHORT_ID_FILE, short_id_list)
        return short_id
