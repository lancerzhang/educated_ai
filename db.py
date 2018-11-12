import time, memory, util, sound, uuid
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
        return self.table.get(Query()[memory.ID] == mid)

    # return None if not found
    def get_memory(self, mid, recall=False):
        mem = self._get_memory(mid)
        if mem is not None:
            memory.refresh(mem, recall, True)
            if mem[memory.STRENGTH] == -1:
                return None
        return mem

    # return None if not found
    def use_memory(self, mid):
        return self.get_memory(mid, True)

    def update_memory(self, fields, mid):
        self.table.update(fields, Query()[memory.ID] == mid)

    def remove_memory(self, mid):
        self.table.remove(Query()[memory.ID] == mid)

    def refresh_memories(self, records, recall=False):
        cleaned = 0
        tobe_removed = []
        for record in records:
            memory.refresh(record, recall, True)
            if record[memory.STRENGTH] == -1:
                cleaned = cleaned + 1
                self.table.remove(Query()[memory.ID] == record[memory.ID])
                tobe_removed.append(record[memory.ID])
        for mid in tobe_removed:
            for record in records:
                if record[memory.ID] == mid:
                    records.remove(record)
                    continue
        return cleaned

    def housekeep(self):
        print 'start to housekeep memory'
        clean_time = time.time() - 60
        query = Query()
        records = self.table.search(query[memory.LAST_RECALL] < clean_time)
        print 'memories to be refresh:', len(records)
        cleaned = self.refresh_memories(records)
        print 'memories were deleted:', cleaned
        return cleaned

    # private method
    def _add_record(self, new_record):
        # new_record = record.copy()
        uid = str(uuid.uuid4())
        new_record.update({memory.ID: uid, memory.STRENGTH: 100, memory.RECALL: 1, memory.LAST_RECALL: time.time()})
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

    # it return new created record id, normally not use it
    def _add_vision(self, addition=None):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.FEATURE_TYPE: memory.VISION, })
        if addition is not None:
            new_memory.update(addition)
        return self._add_record(new_memory)

    def add_vision(self, addition=None):
        mid = self._add_vision(addition)
        return self._get_memory(mid)

    # it return new created record id, normally not use it
    def _add_sound(self, addition=None):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.FEATURE_TYPE: memory.SOUND})
        if addition is not None:
            new_memory.update(addition)
        return self._add_record(new_memory)

    def add_sound(self, addition=None):
        mid = self._add_sound(addition)
        return self._get_memory(mid)

    # it return new created record id, normally not use it
    def _add_action(self, addition=None):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.FEATURE_TYPE: memory.ACTION})
        if addition is not None:
            new_memory.update(addition)
        return self._add_record(new_memory)

    def add_action(self, addition=None):
        mid = self._add_action(addition)
        return self._get_memory(mid)

    def add_parent(self, memories):
        first_data = []
        for mem in memories:
            if not isinstance(mem, Document):
                print mem
            first_data.append(mem[memory.ID])
        # add new memory with those children as first data
        parent = self.add_memory({memory.CHILD_MEM: first_data})
        # update children
        for mem in memories:
            parent_ids = mem[memory.PARENT_MEM]
            if parent[memory.ID] not in parent_ids:
                parent_ids.append(parent[memory.ID])
                self.update_memory({memory.PARENT_MEM: parent_ids}, mem[memory.ID])
        return parent
