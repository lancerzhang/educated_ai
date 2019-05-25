import constants
import sqlite3
import util


class DataSqlite3:
    TABLE_NAME = 'bm'

    def create_tables(self):
        sql_table = '''create table if not exists %s (
                %s text primary key,
                %s integer,
                %s integer,
                %s integer,
                %s integer,
                %s integer,
                %s text,
                %s text,
                %s text,
                %s text,
                %s text,
                %s text,
                %s text,
                %s text,
                %s integer,
                %s integer,
                %s integer,
                %s text,
                %s text
                )''' % (self.TABLE_NAME,
                        constants.MID,
                        constants.STRENGTH,
                        constants.RECALL_COUNT,
                        constants.REWARD,
                        constants.PROTECT_TIME,
                        constants.LAST_RECALL_TIME,
                        constants.PARENT_MEM,
                        constants.CHILD_MEM,
                        constants.VIRTUAL_MEMORY_TYPE,
                        constants.PHYSICAL_MEMORY_TYPE,
                        constants.KERNEL,
                        constants.FEATURE,
                        constants.CHANNEL,
                        constants.CLICK_TYPE,
                        constants.DEGREES,
                        constants.SPEED,
                        constants.MOVE_DURATION,
                        constants.ZOOM_TYPE,
                        constants.ZOOM_DIRECTION)
        self.con.execute(sql_table)

    def __init__(self,path):
        self.con = sqlite3.connect(path)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
        self.create_tables()

    def insert(self, bm):
        columns = ', '.join(bm.keys())
        placeholders = ':' + ', :'.join(bm.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (self.TABLE_NAME, columns, placeholders)
        prepare_data(bm)
        self.cur.execute(query, bm)
        self.con.commit()

    def get_by_id(self, eid):
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_NAME, constants.MID)
        self.cur.execute(query, (eid,))
        return self.cur.fetchone()

    def get_all(self):
        query = 'SELECT * FROM %s ' % self.TABLE_NAME
        self.cur.execute(query)
        records = self.cur.fetchall()
        return records

    def update(self, content, mid):
        params = [key + "=:" + key for key in content]
        updates = ', '.join(params)
        query = 'UPDATE {0} SET {1} WHERE {2}=:{2}'.format(self.TABLE_NAME, updates, constants.MID)
        prepare_data(content)
        content.update({constants.MID: mid})
        self.cur.execute(query, content)
        self.con.commit()

    def remove(self, eid):
        query = 'DELETE FROM %s WHERE %s=?' % (self.TABLE_NAME, constants.MID)
        self.cur.execute(query, (eid,))
        self.con.commit()

    def search_by_last_call(self, last_call):
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_NAME, constants.LAST_RECALL_TIME)
        self.cur.execute(query, (last_call,))
        return self.cur.fetchall()

    def get_eden_memories(self):
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_NAME, constants.RECALL_COUNT)
        self.cur.execute(query, (2,))
        return self.cur.fetchall()

    def get_young_memories(self):
        query = 'SELECT * FROM {0} WHERE {1}>=? AND {1}<? '.format(self.TABLE_NAME, constants.RECALL_COUNT)
        self.cur.execute(query, (2, 20))
        return self.cur.fetchall()

    def get_old_memories(self):
        query = 'SELECT * FROM %s WHERE %s>=?  ' % (self.TABLE_NAME, constants.RECALL_COUNT)
        self.cur.execute(query, (20,))
        return self.cur.fetchall()

    def get_vision_move_memory(self, degrees, speed, duration):
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=? AND %s=?' % (
            self.TABLE_NAME, constants.PHYSICAL_MEMORY_TYPE, constants.DEGREES, constants.SPEED,
            constants.MOVE_DURATION)
        self.cur.execute(query, (constants.VISION_FOCUS_MOVE, degrees, speed, duration))
        return self.cur.fetchone()

    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=?' % (
            self.TABLE_NAME, constants.PHYSICAL_MEMORY_TYPE, constants.ZOOM_TYPE, constants.ZOOM_DIRECTION)
        self.cur.execute(query, (constants.VISION_FOCUS_ZOOM, zoom_type, zoom_direction))
        return self.cur.fetchone()

    def get_mouse_click_memory(self, click_type):
        query = 'SELECT * FROM %s WHERE %s=? AND %s=?' % (
            self.TABLE_NAME, constants.PHYSICAL_MEMORY_TYPE, constants.CLICK_TYPE)
        self.cur.execute(query, (constants.ACTION_MOUSE_CLICK, click_type))
        return self.cur.fetchone()

    def get_by_child_ids(self, child_mem):
        query = 'SELECT * FROM %s WHERE %s=? ' % (self.TABLE_NAME, constants.CHILD_MEM)
        self.cur.execute(query, (util.list_to_sorted_string(child_mem),))
        return self.cur.fetchone()

    def keep_fit(self):
        return


def prepare_data(d):
    if constants.CHILD_MEM in d:
        d.update({constants.CHILD_MEM: util.list_to_sorted_string(d.get(constants.CHILD_MEM))})
    if constants.PARENT_MEM in d:
        d.update({constants.PARENT_MEM: util.list_to_str(d.get(constants.PARENT_MEM))})
    if constants.FEATURE in d:
        d.update({constants.FEATURE: util.list_to_str(d.get(constants.FEATURE))})


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        value = row[idx]
        if value is not None:
            field = col[0]
            if field == constants.CHILD_MEM or field == constants.PARENT_MEM:
                if len(value) > 0:
                    d[field] = row[idx].split(',')
                else:
                    d[field] = []
            elif field == constants.FEATURE:
                d[field] = util.str_to_int_list(value)
            else:
                d[field] = value
    return d
