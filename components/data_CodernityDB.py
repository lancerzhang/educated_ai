import constants, util, hashlib
from CodernityDB.database_super_thread_safe import SuperThreadSafeDatabase
from CodernityDB.hash_index import HashIndex
from CodernityDB.tree_index import TreeBasedIndex
from CodernityDB.database import RecordNotFound
from CodernityDB.database import RecordDeleted
from CodernityDB.database import DatabasePathException


class ChildMemoryIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
from components import constants,util
import hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(ChildMemoryIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        list1 = data.get(constants.CHILD_MEM)
        if list1 is None or len(list1) == 0:
            return None
        else:
            index_str = util.list_to_sorted_string(list1)
            return hashlib.md5(index_str).hexdigest(), None

    def make_key(self, key):
        if key is None or len(key) == 0:
            return None
        else:
            index_str = util.list_to_sorted_string(key)
            return hashlib.md5(index_str).hexdigest()


class ActorMouseIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
from components import constants
import hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(ActorMouseIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        mem_type = data.get(constants.PHYSICAL_MEMORY_TYPE)
        click_type = data.get(constants.CLICK_TYPE)
        if mem_type is None or click_type is None:
            return None
        else:
            return hashlib.md5(mem_type + click_type).hexdigest(), None

    def make_key(self, key):
        mem_type = key.get(constants.PHYSICAL_MEMORY_TYPE)
        click_type = key.get(constants.CLICK_TYPE)
        if mem_type is None or click_type is None:
            return None
        else:
            return hashlib.md5(mem_type + click_type).hexdigest()


class VisionZoomIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
from components import constants
import hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(VisionZoomIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        mem_type = data.get(constants.PHYSICAL_MEMORY_TYPE)
        zoom_type = data.get(constants.ZOOM_TYPE)
        zoom_direction = data.get(constants.ZOOM_DIRECTION)
        if mem_type is None or zoom_type is None or zoom_direction is None:
            return None
        else:
            return hashlib.md5(mem_type + zoom_type + zoom_direction).hexdigest(), None

    def make_key(self, key):
        mem_type = key.get(constants.PHYSICAL_MEMORY_TYPE)
        zoom_type = key.get(constants.ZOOM_TYPE)
        zoom_direction = key.get(constants.ZOOM_DIRECTION)
        if mem_type is None or zoom_type is None or zoom_direction is None:
            return None
        else:
            return hashlib.md5(mem_type + zoom_type + zoom_direction).hexdigest()


class VisionMoveIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
from components import constants
import hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(VisionMoveIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        mem_type = data.get(constants.PHYSICAL_MEMORY_TYPE)
        degrees = str(data.get(constants.DEGREES))
        speed = str(data.get(constants.SPEED))
        duration = str(data.get(constants.MOVE_DURATION))
        if mem_type is None or degrees is None or speed is None or duration is None:
            return None
        else:
            return hashlib.md5(mem_type + degrees + speed + duration).hexdigest(), None

    def make_key(self, key):
        mem_type = key.get(constants.PHYSICAL_MEMORY_TYPE)
        degrees = str(key.get(constants.DEGREES))
        speed = str(key.get(constants.SPEED))
        duration = str(key.get(constants.MOVE_DURATION))
        if mem_type is None or degrees is None or speed is None or duration is None:
            return None
        else:
            return hashlib.md5(mem_type + degrees + speed + duration).hexdigest()


class HousekeepIndex(HashIndex):
    sh_num = 100
    custom_header = """from CodernityDB.hash_index import HashIndex
from components import constants
import hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = 'I'
        super(HousekeepIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        lcl = data.get(constants.LAST_RECALL_TIME)
        if lcl is None:
            return None
        else:
            return int(lcl) % self.sh_num, None

    def make_key(self, key):
        return int(key) % self.sh_num


class RecallIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
from components import constants"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = 'I'
        super(RecallIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        recall = data.get(constants.RECALL_COUNT)
        if recall is None:
            return None
        else:
            return recall, None

    def make_key(self, key):
        return key


class LastRecallIndex(TreeBasedIndex):
    custom_header = """from CodernityDB.tree_index import TreeBasedIndex
from components import constants"""

    def __init__(self, *args, **kwargs):
        kwargs['node_capacity'] = 13
        kwargs['key_format'] = 'L'
        super(LastRecallIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get(constants.LAST_RECALL_TIME)
        if a_val is not None:
            return a_val, None
        return None

    def make_key(self, key):
        return key


class DataCodernityDB:
    INDEX_RECALL = 'recall'
    INDEX_LAST_RECALL = 'last_recall'
    INDEX_VISION_MOVE = 'vision_move'
    INDEX_VISION_ZOOM = 'vision_zoom'
    INDEX_ACTOR_MOUSE = 'actor_mouse'
    INDEX_CHILD_MEMORY = 'child_memory'
    INDEX_HOUSEKEEP = 'housekeep'
    db = None

    def __init__(self, folder='CodernityDB'):
        self.db = SuperThreadSafeDatabase(folder)
        try:
            self.db.open()
        except DatabasePathException:
            self.db.create()
            # strange error when use tree index, disable it first
            self.db.add_index(LastRecallIndex(self.db.path, self.INDEX_LAST_RECALL))
            self.db.add_index(RecallIndex(self.db.path, self.INDEX_RECALL))
            self.db.add_index(VisionMoveIndex(self.db.path, self.INDEX_VISION_MOVE))
            self.db.add_index(VisionZoomIndex(self.db.path, self.INDEX_VISION_ZOOM))
            self.db.add_index(ActorMouseIndex(self.db.path, self.INDEX_ACTOR_MOUSE))
            self.db.add_index(ChildMemoryIndex(self.db.path, self.INDEX_CHILD_MEMORY))
            self.db.add_index(HousekeepIndex(self.db.path, self.INDEX_HOUSEKEEP))

    def insert(self, content):
        content.update({'_id': content.get(constants.MID)})
        record = self.db.insert(content)
        doc = self.db.get('id', record.get('_id'))
        return doc

    def get_by_id(self, eid):
        try:
            record = self.db.get('id', eid, with_doc=True)
            return record
        except  RecordNotFound:
            return None
        except RecordDeleted:
            return None

    def get_all(self):
        records = self.db.all('id', with_doc=True)
        results = [x for x in records]
        return results

    def update(self, content, eid):
        try:
            record = self.db.get('id', eid)
            record.update(content)
            return self.db.update(record)
        except  RecordNotFound:
            return None
        except RecordDeleted:
            return None

    def remove(self, eid):
        try:
            record = self.db.get('id', eid)
            return self.db.delete(record)
        except  RecordNotFound:
            return None
        except RecordDeleted:
            return None

    def search_by_last_call(self, last_call):
        records = []
        # if add "start=0", there is a problem that sometimes get_many can't retrieve doc
        # error is "RecordNotFound: Location '                              l' not found"
        # as the doc is not exist, don't know why
        db_records = self.db.get_many(self.INDEX_LAST_RECALL, end=last_call, with_doc=True)
        for record in db_records:
            records.append(record.get('doc'))
        return records

    def search_housekeep(self, sh_num):
        records = []
        db_records = self.db.get_many(self.INDEX_HOUSEKEEP, sh_num, with_doc=True)
        for record in db_records:
            records.append(record.get('doc'))
        return records

    def get_eden_memories(self):
        total_records = []
        for recall in range(0, 2):
            records = self.get_recall(recall)
            total_records = total_records + records
        return total_records

    def get_young_memories(self):
        total_records = []
        for recall in range(2, 20):
            records = self.get_recall(recall)
            total_records = total_records + records
        return total_records

    def get_old_memories(self):
        total_records = []
        for recall in range(20, 100):
            records = self.get_recall(recall)
            total_records = total_records + records
        return total_records

    def get_recall(self, recall):
        records = []
        try:
            db_records = self.db.get_many(self.INDEX_RECALL, recall, with_doc=True)
            for record in db_records:
                records.append(record.get('doc'))
        except RecordNotFound:
            return records
        except RecordDeleted:
            return records
        return records

    def get_vision_move_memory(self, degrees, speed, duration):
        try:
            record = self.db.get(self.INDEX_ACTOR_MOUSE,
                                 {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE,
                                  constants.DEGREES: degrees, constants.SPEED: speed,
                                  constants.MOVE_DURATION: duration},
                                 with_doc=True)
            return record.get('doc')
        except RecordNotFound:
            return None

    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        try:
            record = self.db.get(self.INDEX_ACTOR_MOUSE,
                                 {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_ZOOM,
                                  constants.ZOOM_TYPE: zoom_type, constants.ZOOM_DIRECTION: zoom_direction},
                                 with_doc=True)
            return record.get('doc')
        except RecordNotFound:
            return None

    def get_mouse_click_memory(self, click_type):
        try:
            record = self.db.get(self.INDEX_ACTOR_MOUSE,
                                 {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_MOUSE_CLICK,
                                  constants.CLICK_TYPE: click_type}, with_doc=True)
            return record.get('doc')
        except RecordNotFound:
            return None

    def get_by_child_ids(self, id_list):
        try:
            record = self.db.get(self.INDEX_CHILD_MEMORY, id_list, with_doc=True)
            return record.get('doc')
        except RecordNotFound:
            return None

    def keep_fit(self):
        self.db.compact()
