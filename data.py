import time, uuid, memory, constants


class Data:
    db = None

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
        self.db.update(content, mid)

    def remove_memory(self, mid):
        self.db.remove(mid)

    def refresh_memories(self, records, recall=False):
        cleaned = 0
        tobe_removed = []
        for record in records:
            memory.refresh(record, recall, True)
            if record[constants.STRENGTH] == -1:
                cleaned = cleaned + 1
                self.remove_memory(record[constants.MID])
                tobe_removed.append(record[constants.MID])
        for mid in tobe_removed:
            for record in records:
                if record[constants.MID] == mid:
                    records.remove(record)
                    continue
        return cleaned

    def housekeep(self):
        print 'start to housekeep memory'
        clean_time = time.time() - 60
        clean_time = int(clean_time)
        records = self.db.search_by_last_call(clean_time)
        print 'memories to be refresh:', len(records)
        cleaned = self.refresh_memories(records)
        print 'memories were deleted:', cleaned
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
        return self._get_memory(mid)

    def search_vision_movement(self, degrees, speed, duration):
        records = self.db.search_vision_movement(degrees, speed, duration)
        self.refresh_memories(records, True)
        return records

    def search_vision_zoom(self, zoom_type):
        records = self.db.search_vision_zoom(zoom_type)
        self.refresh_memories(records, True)
        return records

    def search_actor_mouse(self, click_type):
        records = self.db.search_actor_mouse(click_type)
        self.refresh_memories(records, True)
        return records
