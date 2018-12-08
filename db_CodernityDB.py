import constants, util, hashlib
from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex
from CodernityDB.tree_index import TreeBasedIndex
from CodernityDB.database import RecordNotFound
from CodernityDB.database import DatabaseException


class ChildMemoryIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
import constants,util,hashlib"""

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
import constants,hashlib"""

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
import constants,hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(VisionZoomIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        mem_type = data.get(constants.PHYSICAL_MEMORY_TYPE)
        zoom_type = data.get(constants.ZOOM_TYPE)
        if mem_type is None or zoom_type is None:
            return None
        else:
            return hashlib.md5(mem_type + zoom_type).hexdigest(), None

    def make_key(self, key):
        mem_type = key.get(constants.PHYSICAL_MEMORY_TYPE)
        zoom_type = key.get(constants.ZOOM_TYPE)
        if mem_type is None or zoom_type is None:
            return None
        else:
            return hashlib.md5(mem_type + zoom_type).hexdigest()


class VisionMoveIndex(HashIndex):
    custom_header = """from CodernityDB.hash_index import HashIndex
import constants,hashlib"""

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(VisionMoveIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        mem_type = data.get(constants.PHYSICAL_MEMORY_TYPE)
        degrees = str(data.get(constants.DEGREES))
        speed = str(data.get(constants.SPEED))
        duration = str(data.get(constants.DURATION))
        if mem_type is None or degrees is None or speed is None or duration is None:
            return None
        else:
            return hashlib.md5(mem_type + degrees + speed + duration).hexdigest(), None

    def make_key(self, key):
        mem_type = key.get(constants.PHYSICAL_MEMORY_TYPE)
        degrees = str(key.get(constants.DEGREES))
        speed = str(key.get(constants.SPEED))
        duration = str(key.get(constants.DURATION))
        if mem_type is None or degrees is None or speed is None or duration is None:
            return None
        else:
            return hashlib.md5(mem_type + degrees + speed + duration).hexdigest()


class LastRecallIndex(TreeBasedIndex):
    custom_header = """from CodernityDB.tree_index import TreeBasedIndex
import constants"""

    def __init__(self, *args, **kwargs):
        kwargs['node_capacity'] = 13
        kwargs['key_format'] = 'I'
        super(LastRecallIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get(constants.LAST_RECALL)
        if a_val is not None:
            return a_val, None
        return None

    def make_key(self, key):
        return key


class DB_CodernityDB:
    INDEX_LAST_RECALL = 'last_recall'
    INDEX_VISION_MOVE = 'vision_move'
    INDEX_VISION_ZOOM = 'vision_zoom'
    INDEX_ACTOR_MOUSE = 'actor_mouse'
    INDEX_CHILD_MEMORY = 'child_memory'
    db = None

    def __init__(self, folder='CodernityDB'):
        self.db = Database(folder)
        try:
            self.db.open()
        except:
            self.db.create()
            self.db.add_index(LastRecallIndex(self.db.path, self.INDEX_LAST_RECALL))
            self.db.add_index(VisionMoveIndex(self.db.path, self.INDEX_VISION_MOVE))
            self.db.add_index(VisionZoomIndex(self.db.path, self.INDEX_VISION_ZOOM))
            self.db.add_index(ActorMouseIndex(self.db.path, self.INDEX_ACTOR_MOUSE))
            self.db.add_index(ChildMemoryIndex(self.db.path, self.INDEX_CHILD_MEMORY))

    def insert(self, content):
        content.update({'_id': content.get(constants.MID)})
        record = self.db.insert(content)
        doc = self.db.get('id', record.get('_id'))
        return doc

    def get_by_id(self, eid):
        try:
            record = self.db.get('id', eid)
        except DatabaseException:
            record = None
        return record

    def get_all(self):
        records = self.db.all('id', with_doc=True)
        results = [x for x in records]
        return results

    def update(self, content, eid):
        try:
            record = self.db.get('id', eid)
        except DatabaseException:
            record = None
        if record is not None:
            record.update(content)
            updated = self.db.update(record)
            return updated

    def remove(self, eid):
        try:
            record = self.db.get('id', eid)
        except DatabaseException:
            record = None
        if record is not None:
            return self.db.delete(record)

    def search_by_last_call(self, last_call):
        records = []
        # if add "start=0", there is a problem that sometimes get_many can't retrieve doc
        # error is "RecordNotFound: Location '                              l' not found"
        # as the doc is not exist, don't know why
        db_records = self.db.get_many(self.INDEX_LAST_RECALL, end=last_call, with_doc=True)
        for record in db_records:
            records.append(record.get('doc'))
        return records

    def get_vision_move_memory(self, degrees, speed, duration):
        try:
            record = self.db.get(self.INDEX_ACTOR_MOUSE,
                                 {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE,
                                  constants.DEGREES: degrees, constants.SPEED: speed, constants.DURATION: duration})
            doc = record.get('doc')
        except RecordNotFound:
            doc = None
        return doc

    def get_vision_zoom_memory(self, zoom_type):
        try:
            record = self.db.get(self.INDEX_ACTOR_MOUSE,
                                 {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_ZOOM,
                                  constants.ZOOM_TYPE: zoom_type})
            doc = record.get('doc')
        except RecordNotFound:
            doc = None
        return doc

    def get_actor_mouse_memory(self, click_type):
        try:
            record = self.db.get(self.INDEX_ACTOR_MOUSE,
                                 {constants.PHYSICAL_MEMORY_TYPE: constants.ACTOR_MOUSE,
                                  constants.CLICK_TYPE: click_type})
            doc = record.get('doc')
        except RecordNotFound:
            doc = None
        return doc

    def get_child_memory(self, child_mem):
        try:
            record = self.db.get(self.INDEX_CHILD_MEMORY, child_mem,with_doc=True)
            doc = record.get('doc')
        except RecordNotFound:
            doc = None
        return doc
