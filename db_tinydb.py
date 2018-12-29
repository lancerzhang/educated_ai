import constants, uuid
from tinydb import Query
from tinydb_smartcache import SmartCacheTable
from tinydb.database import Document


class DB_TinyDB:
    db_instance = None
    table = None

    def __init__(self, db):
        self.db_instance = db
        # has strange error when use cache table
        # self.db_instance.table_class = SmartCacheTable
        self.table = self.db_instance.table('Memory')

    def insert(self, content):
        self.table.insert(content)

    def get_by_id(self, eid):
        return self.table.get(Query()[constants.MID] == eid)

    def get_all(self):
        return self.table.all()

    def update(self, content, eid):
        self.table.update(content, Query()[constants.MID] == eid)

    def remove(self, eid):
        self.table.remove(Query()[constants.MID] == eid)

    def search_by_last_call(self, last_call):
        query = Query()
        return self.table.search(query[constants.LAST_RECALL] < last_call)

    def get_vision_move_memory(self, degrees, speed, duration):
        query = Query()
        return self.table.search(
            (query[constants.PHYSICAL_MEMORY_TYPE] == constants.VISION_FOCUS_MOVE) & (
                    query[constants.DEGREES] == degrees) & (
                    query[constants.SPEED] == speed) & (query[constants.DURATION] == duration))

    def get_vision_zoom_memory(self, zoom_type):
        query = Query()
        return self.table.search((query[constants.PHYSICAL_MEMORY_TYPE] == constants.VISION_FOCUS_ZOOM) & (
                query[constants.ZOOM_TYPE] == zoom_type))

    def get_actor_mouse_memory(self, click_type):
        query = Query()
        return self.table.search((query[constants.PHYSICAL_MEMORY_TYPE] == constants.ACTOR_MOUSE) & (
                query[constants.CLICK_TYPE] == click_type))

    def get_child_memory(self, child_mem):
        return None