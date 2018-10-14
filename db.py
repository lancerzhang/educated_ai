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
    def _get_memory(self, id):
        return self.table.get(Query()[memory.ID] == id)

    # return None if not found
    def get_memory(self, id, recall=False):
        mem = self._get_memory(id)
        if mem is not None:
            memory.refresh(mem, recall)
            if mem[memory.STRENGTH] == -1:
                return None
        return mem

    # return None if not found
    def use_memory(self, id):
        return self.get_memory(id, True)

    def update_memory(self, fields, id):
        self.table.update(fields, Query()[memory.ID] == id)

    def remove_memory(self, id):
        self.table.remove(Query()[memory.ID] == id)

    def refresh_memories(self, records, recall=False):
        cleaned = 0
        tobe_removed = []
        for record in records:
            memory.refresh(record, recall)
            if record[memory.STRENGTH] == -1:
                cleaned = cleaned + 1
                self.table.remove(Query()[memory.ID] == record[memory.ID])
                tobe_removed.append(record[memory.ID])
        for id in tobe_removed:
            for record in records:
                if record[memory.ID] == id:
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
        id = str(uuid.uuid4())
        new_record.update({memory.ID: id, memory.STRENGTH: 100, memory.RECALL: 1, memory.LAST_RECALL: time.time()})
        self.table.insert(new_record)
        return id

    # it return new created record id, normally not use it
    def _add_memory(self, addition={}):
        new_memory = memory.BASIC_MEMORY.copy()
        # use children memories to match the experience
        new_memory.update({memory.TYPE: memory.COLLECTION})
        new_memory.update(addition)
        return self._add_record(new_memory)

    def add_memory(self, addition={}):
        eid = self._add_memory(addition)
        return self._get_memory(eid)

    # it return new created record id, normally not use it
    def _add_vision(self, addition={}):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.TYPE: memory.VISION, })
        new_memory.update(addition)
        return self._add_record(new_memory)

    def add_vision(self, addition={}):
        eid = self._add_vision(addition)
        return self._get_memory(eid)

    # it return new created record id, normally not use it
    def _add_sound(self, addition={}):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.TYPE: memory.SOUND})
        new_memory.update(addition)
        return self._add_record(new_memory)

    def add_sound(self, addition={}):
        eid = self._add_sound(addition)
        return self._get_memory(eid)

    # it return new created record id, normally not use it
    def _add_focus(self, addition={}):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.TYPE: memory.FOCUS, 'angle': 10, 'speed': 10, 'duration': 10})
        new_memory.update(addition)
        return self._add_record(new_memory)

    # it return new created record id, normally not use it
    def _add_speak(self, addition={}):
        new_memory = memory.BASIC_MEMORY.copy()
        new_memory.update({memory.TYPE: memory.SPEAK, 'word': 'yes'})
        new_memory.update(addition)
        return self._add_record(new_memory)

    # do not use directly, we usually need to refresh it before getting it
    # return [] if not found
    def _search_sound(self, feature, name, min, max):
        query = Query()
        records = self.table.search((query[memory.TYPE] == memory.SOUND) & (query[sound.FEATURE] == feature) & (query[name].test(util.between, min, max)))
        return records

    def _search_sound2(self, feature, index_value, name, min, max):
        query = Query()
        records = self.table.search(
            (query[memory.TYPE] == memory.SOUND) & (query[sound.FEATURE] == feature) & (query[sound.INDEX] == index_value) & (query[name].test(util.between, min, max)))
        return records

    # TODO, need to remove all references?
    def search_sound(self, feature, name, min, max, recall=False):
        records = self._search_sound2(feature, name, min, max)
        self.refresh_memories(records, recall)
        return records

    def search_sound2(self, feature, index, value, min, max, recall=False):
        records = self._search_sound2(feature, index, value, min, max)
        self.refresh_memories(records, recall)
        return records

    def use_sound(self, feature, name, min, max):
        return self.search_sound(feature, name, min, max, True)

    def use_sound2(self, feature, index, value, min, max):
        return self.search_sound2(feature, index, value, min, max, True)

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
