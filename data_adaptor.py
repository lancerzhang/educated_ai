import time, uuid, memory, constants, util, thread


class DataAdaptor:
    is_log = False
    start_thread = True
    seq = 0

    def __init__(self, db):
        self.db = db

    # return None if not found
    # do not use directly, we usually need to refresh it before getting it
    def _get_memory(self, mid):
        return self.db.get_by_id(mid)

    # return None if not found
    def get_memory(self, mid, recall=False):
        mem = self._get_memory(mid)
        if mem is not None:
            memory.refresh(mem, recall, True)
            if mem[constants.STRENGTH] == -1:
                self.remove_memory(mem[constants.MID])
                return None
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
            memory.refresh(mem, recall, True)
            if mem[constants.STRENGTH] == -1:
                self.remove_memory(mem[constants.MID])
            else:
                live_memories.append(mem)
        return live_memories

    def cleanup_fields(self):
        self.cleanup_field(constants.PARENT_MEM)

    def cleanup_field(self, field):
        start = time.time()
        print 'start to cleanup_fields', field
        memories = self.db.get_all()
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
                if self.is_log:
                    print 'clean up from ', len(original_list), ' to ', len(new_list)
                self.update_memory({field: new_list}, mem[constants.MID])
        print 'cleanup_fields used time ' + str(time.time() - start)

    # def schedule_housekeep(self):
    #     self.seq = self.seq + 1
    #     while self.start_thread:
    #         self.full_housekeep()
    #         time.sleep(30)

    def gc(self, gc_type):
        start = time.time()
        print '\nstart to gc ', gc_type, ' memory'
        if gc_type is constants.EDEN:
            records = self.db.get_eden_memories()
        elif gc_type is constants.YOUNG:
            records = self.db.get_young_memories()
        elif gc_type is constants.OLD:
            records = self.db.get_old_memories()
        else:
            records = self.db.get_all()
        print 'memories to be refresh:', len(records)
        lives = self.refresh_memories(records)
        if records is None:
            cleaned = 0
        elif lives is None:
            cleaned = len(records)
        else:
            cleaned = len(records) - len(lives)
        print 'memories were deleted:', cleaned
        print gc_type, ' gc used time ' + str(time.time() - start)
        return cleaned

    def full_gc(self):
        return self.gc('full')

    def partial_gc(self):
        self.seq = self.seq + 1
        start = time.time()
        if self.is_log:
            print '\nstart to partial housekeep memory'
        records = self.db.search_housekeep(self.seq % 100)
        if self.is_log:
            print 'memories to be refresh:', len(records)
        lives = self.refresh_memories(records)
        if records is None:
            cleaned = 0
        elif lives is None:
            cleaned = len(records)
        else:
            cleaned = len(records) - len(lives)
        if self.is_log:
            print 'memories were deleted:', cleaned
            print 'partial_housekeep used time ' + str(time.time() - start)
        return cleaned

    # private method
    def _add_record(self, content):
        uid = str(uuid.uuid4())
        uid = uid.replace('-', '')
        content.update(
            {constants.MID: uid, constants.STRENGTH: 100, constants.RECALL: 1, constants.LAST_RECALL: int(time.time())})
        record = self.db.insert(content)
        return uid

    # it return new created record id, normally not use it
    def _add_memory(self, addition=None):
        new_memory = memory.BASIC_MEMORY.copy()
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

    def get_vision_zoom_memory(self, zoom_type):
        record = self.db.get_vision_zoom_memory(zoom_type)
        return record

    def get_action_mouse_memory(self, click_type):
        record = self.db.get_action_mouse_memory(click_type)
        return record

    def get_child_memory(self, child_mem):
        record = self.db.get_child_memory(child_mem)
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
                    # print memories[i]
                    # print memories[j]
                    # print ' '
                    count = count + 1
                    break
        return count
