import time, memory
from tinydb import  Query
from tinydb_smartcache import SmartCacheTable


class Database:
    db_instance = None
    table = None

    def __init__(self, db):
        self.db_instance = db
        self.db_instance.table_class = SmartCacheTable
        self.table = self.db_instance.table('Memory')

    def load_memory(self):
        print 'load memory'

    def get_memory(self,elid):
        return self.table.get(eid=elid)

    def cleanup_memory(self):
        print 'start to cleanup memory'
        clean_time = time.time() - 60
        Memory = Query()
        records=self.table.search( Memory.lastRecall < clean_time)
        print 'memories to cleanup:',len(records)
        cleaned=0
        for record in records:
            memory.refresh(record)
            if record['strength'] == -1:
                cleaned=cleaned+1
                self.table.remove(eids=[record.doc_id])
        print 'memories were cleaned up:', cleaned
        return cleaned

    def add_record(self, record):
        new_record = record.copy()
        new_record.update({'lastRecall': time.time()})
        return self.table.insert(new_record)

    def add_memory(self, addition={}):
        new_memory = memory.basic_memory.copy()
        # use children memories to match the experience
        new_memory.update({'type': 'memory'})
        # new_memory.update({'type': 'memory', 'children': [0, 0]})
        new_memory.update(addition)
        return self.add_record(new_memory)

    def add_vision(self, addition={}):
        new_memory = memory.basic_memory.copy()
        new_memory.update({'type': 'vision', 'filter': 'vf1', 'data': 'abc'})
        return self.add_record(new_memory)

    def add_sound(self, addition={}):
        new_memory = memory.basic_memory.copy()
        new_memory.update({'type': 'sound', 'data': '123'})
        return self.add_record(new_memory)

    def add_focus(self, addition={}):
        new_memory = memory.basic_memory.copy()
        new_memory.update({'type': 'focus', 'angle': 10, 'speed': 10, 'duration': 10})
        return self.add_record(new_memory)

    def add_speak(self, addition={}):
        new_memory = memory.basic_memory.copy()
        new_memory.update({'type': 'speak', 'word': 'yes'})
        return self.add_record(new_memory)

