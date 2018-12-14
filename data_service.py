import time, uuid, memory, constants, util, thread


class DataService:
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

    # def schedule_housekeep(self):
    #     self.seq = self.seq + 1
    #     while self.start_thread:
    #         self.full_housekeep()
    #         time.sleep(30)

    def full_housekeep(self):
        start = time.time()
        print '\nstart to full housekeep memory'
        records = self.db.get_all()
        print 'memories to be refresh:', len(records)
        lives = self.refresh_memories(records)
        if records is None:
            cleaned = 0
        elif lives is None:
            cleaned = len(records)
        else:
            cleaned = str(len(records) - len(lives))
        print 'memories were deleted:', cleaned
        print 'full_housekeep used time ' + str(time.time() - start)
        return cleaned

    def partial_housekeep(self):
        self.seq = self.seq + 1
        start = time.time()
        print '\nstart to partial housekeep memory'
        records = self.db.search_housekeep(self.seq % 100)
        print 'memories to be refresh:', len(records)
        lives = self.refresh_memories(records)
        if records is None:
            cleaned = 0
        elif lives is None:
            cleaned = len(records)
        else:
            cleaned = len(records) - len(lives)
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

    def get_actor_mouse_memory(self, click_type):
        record = self.db.get_actor_mouse_memory(click_type)
        return record

    def get_child_memory(self, child_mem):
        record = self.db.get_child_memory(child_mem)
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
