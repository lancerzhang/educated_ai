import time, uuid, memory, constants
from tinydb import Query
from tinydb_smartcache import SmartCacheTable
from tinydb.database import Document


class Database:
    db_instance = None
    table = None

    def __init__(self, db):
        self.db_instance = db
        # has strange error when use cache table
        # self.db_instance.table_class = SmartCacheTable
        self.table = self.db_instance.table('Memory')

    def load_memory(self):
        print 'load memory'

    # return None if not found
    # do not use directly, we usually need to refresh it before getting it
    def _get_memory(self, mid):
        return self.table.get(Query()[constants.ID] == mid)

    # return None if not found
    def get_memory(self, mid, recall=False):
        mem = self._get_memory(mid)
        if mem is not None:
            memory.refresh(mem, recall, True)
            if mem[constants.STRENGTH] == -1:
                return None
        return mem

    # return None if not found
    def use_memory(self, mid):
        return self.get_memory(mid, True)

    def update_memory(self, fields, mid):
        self.table.update(fields, Query()[constants.ID] == mid)

    def remove_memory(self, mid):
        self.table.remove(Query()[constants.ID] == mid)

    def refresh_memories(self, records, recall=False):
        cleaned = 0
        tobe_removed = []
        for record in records:
            memory.refresh(record, recall, True)
            if record[constants.STRENGTH] == -1:
                cleaned = cleaned + 1
                self.table.remove(Query()[constants.ID] == record[constants.ID])
                tobe_removed.append(record[constants.ID])
        for mid in tobe_removed:
            for record in records:
                if record[constants.ID] == mid:
                    records.remove(record)
                    continue
        return cleaned

    def housekeep(self):
        print 'start to housekeep memory'
        clean_time = time.time() - 60
        query = Query()
        records = self.table.search(query[constants.LAST_RECALL] < clean_time)
        print 'memories to be refresh:', len(records)
        cleaned = self.refresh_memories(records)
        print 'memories were deleted:', cleaned
        return cleaned

    # private method
    def _add_record(self, new_record):
        # new_record = record.copy()
        uid = str(uuid.uuid4())
        new_record.update(
            {constants.ID: uid, constants.STRENGTH: 100, constants.RECALL: 1, constants.LAST_RECALL: time.time()})
        self.table.insert(new_record)
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

    # do not use directly, we usually need to refresh it before getting it
    # return [] if not found
    def _search_vision_movement(self, degrees, speed, duration):
        query = Query()
        records = self.table.search(
            (query[constants.PHYSICAL_MEMORY_TYPE] == constants.VISION_FOCUS_MOVE) & (
                        query[constants.DEGREES] == degrees) & (
                    query[constants.SPEED] == speed) & (query[constants.DURATION] == duration))
        return records

    def search_vision_movement(self, degrees, speed, duration, recall=False):
        records = self._search_vision_movement(degrees, speed, duration)
        self.refresh_memories(records, recall)
        return records

    def _search_vision_zoom(self, zoom_type):
        query = Query()
        records = self.table.search((query[constants.PHYSICAL_MEMORY_TYPE] == constants.VISION_FOCUS_ZOOM) & (
                    query[constants.ZOOM_TYPE] == zoom_type))
        return records

    def search_vision_zoom(self, zoom_type, recall=False):
        records = self._search_vision_zoom(zoom_type)
        self.refresh_memories(records, recall)
        return records

    def _search_actor_mouse(self, click_type):
        query = Query()
        records = self.table.search((query[constants.PHYSICAL_MEMORY_TYPE] == constants.ACTOR_MOUSE) & (
                    query[constants.CLICK_TYPE] == click_type))
        return records

    def search_actor_mouse(self, click_type, recall=False):
        records = self._search_actor_mouse(click_type)
        self.refresh_memories(records, recall)
        return records