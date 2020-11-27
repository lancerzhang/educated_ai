import logging
import os
import sqlite3

from . import constants
from . import util

logger = logging.getLogger('DataSqlite3')
logger.setLevel(logging.INFO)


class DataSqlite3:
    con = None
    CONN_STR = 'file:database?mode=memory&cache=shared'
    DUMP_FILE = ''
    TABLE_BM = 'bm'
    TABLE_VISION_USED_KERNEL = 'vuk'
    TABLE_SOUND_USED_KERNEL = 'suk'
    TABLE_USED_SPEED = 'spd'
    TABLE_USED_DEGREES = 'dgr'
    TABLE_USED_CHANNEL = 'cnl'
    TABLE_SHORT_ID = 'sid'
    SQL_RETRY_INTERVAL = 0.001
    SQL_RETRY_COUNT = 100

    @util.timeit
    def create_tables(self):
        sql_table = '''create table if not exists %s (
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                %s text,
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
                )''' % (self.TABLE_BM,
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
        self.con.execute(
            'create table if not exists %s (%s text primary key, %s integer)' % (
                self.TABLE_VISION_USED_KERNEL, constants.KERNEL, constants.COUNT))
        self.con.execute(
            'create table if not exists %s (%s text primary key, %s integer)' % (
                self.TABLE_SOUND_USED_KERNEL, constants.KERNEL, constants.COUNT))
        self.con.execute(
            'create table if not exists %s (%s text primary key, %s integer)' % (
                self.TABLE_USED_SPEED, constants.SPEED, constants.COUNT))
        self.con.execute(
            'create table if not exists %s (%s text primary key, %s integer)' % (
                self.TABLE_USED_DEGREES, constants.DEGREES, constants.COUNT))
        self.con.execute(
            'create table if not exists %s (%s text primary key, %s integer)' % (
                self.TABLE_USED_CHANNEL, constants.CHANNEL, constants.COUNT))
        self.con.execute(
            'create table if not exists %s (id INTEGER PRIMARY KEY AUTOINCREMENT, %s text)' % (
                self.TABLE_SHORT_ID, constants.MID))
        self.con.commit()

    @util.timeit
    def connect_db(self):
        self.con = sqlite3.connect(self.CONN_STR, check_same_thread=False, uri=True)
        self.con.execute("PRAGMA read_uncommitted = true;")

    @util.timeit
    def __init__(self, path, init=True):
        self.DUMP_FILE = path
        if not init:
            logging.info('2nd connection of db')
            self.connect_db()
            return

        if os.path.exists(path):
            self.import_from_script(path)
        else:
            logging.info('init db')
            self.connect_db()
            self.create_tables()

    @util.timeit
    def execute(self, *args, **kwargs):
        c = self.con.cursor()
        c.execute(*args, **kwargs)
        self.con.commit()

    @util.timeit
    def executemany(self, *args, **kwargs):
        c = self.con.cursor()
        c.executemany(*args, **kwargs)
        self.con.commit()

    @util.timeit
    def fetchone(self, *args, **kwargs):
        cur = self.con.cursor()
        cur.execute(*args, **kwargs)
        record = cur.fetchone()
        return record

    @util.timeit
    def fetchall(self, *args, **kwargs):
        cur = self.con.cursor()
        cur.execute(*args, **kwargs)
        records = cur.fetchall()
        return records

    @util.timeit
    def insert(self, bm):
        columns = ', '.join(list(bm.keys()))
        placeholders = ':' + ', :'.join(list(bm.keys()))
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (self.TABLE_BM, columns, placeholders)
        prepare_data(bm)
        self.execute(query, bm)

    @util.timeit
    def get_insert(self, bm):
        self.insert(bm)
        return self.get_by_id(bm[constants.MID])

    @util.timeit
    def get_by_id(self, mid):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_BM, constants.MID)
        return self.fetchone(query, (mid,))

    @util.timeit
    def get_all(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s ' % self.TABLE_BM
        return self.fetchall(query)

    @util.timeit
    def update_memory(self, content, mid):
        params = [key + "=:" + key for key in content]
        updates = ', '.join(params)
        query = 'UPDATE {0} SET {1} WHERE {2}=:{2}'.format(self.TABLE_BM, updates, constants.MID)
        prepare_data(content)
        content.update({constants.MID: mid})
        self.execute(query, content)

    @util.timeit
    def update_memories(self, contents):
        params = [key + "=:" + key for key in contents[0]]
        updates = ', '.join(params)
        query = 'UPDATE {0} SET {1} WHERE {2}=:{2}'.format(self.TABLE_BM, updates, constants.MID)
        for content in contents:
            prepare_data(content)
        self.executemany(query, contents)

    @util.timeit
    def delete_memory(self, eid):
        query = 'DELETE FROM %s WHERE %s=?' % (self.TABLE_BM, constants.MID)
        self.execute(query, (eid,))

    @util.timeit
    def delete_memories(self, eids):
        query = 'DELETE FROM %s WHERE %s=?' % (self.TABLE_BM, constants.MID)
        self.executemany(query, list_many(eids))
        logging.debug('delete_memories %s records.' % len(eids))

    @util.timeit
    def search_by_last_call(self, last_call):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_BM, constants.LAST_RECALL_TIME)
        return self.fetchall(query, (last_call,))

    @util.timeit
    def search_all(self, query):
        self.con.row_factory = bm_dict_factory
        return self.fetchall(query)

    @util.timeit
    def get_eden_memories(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_BM, constants.RECALL_COUNT)
        return self.fetchall(query, (2,))

    @util.timeit
    def get_young_memories(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM {0} WHERE {1}>=? AND {1}<? '.format(self.TABLE_BM, constants.RECALL_COUNT)
        return self.fetchall(query, (2, 20))

    @util.timeit
    def get_old_memories(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s>=?  ' % (self.TABLE_BM, constants.RECALL_COUNT)
        return self.fetchall(query, (20,))

    @util.timeit
    def get_memories_by_id_mod(self, mod):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE _id%%10=?  ' % self.TABLE_BM
        return self.fetchall(query, (mod,))

    @util.timeit
    def get_vision_move_memory(self, degrees, speed, duration):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.DEGREES, constants.SPEED,
            constants.MOVE_DURATION)
        return self.fetchone(query, (constants.VISION_FOCUS_MOVE, degrees, speed, duration))

    @util.timeit
    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.ZOOM_TYPE, constants.ZOOM_DIRECTION)
        return self.fetchone(query, (constants.VISION_FOCUS_ZOOM, zoom_type, zoom_direction))

    @util.timeit
    def get_mouse_click_memory(self, click_type):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.CLICK_TYPE)
        return self.fetchone(query, (constants.ACTION_MOUSE_CLICK, click_type))

    @util.timeit
    def get_by_child_ids(self, child_mem):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? ' % (self.TABLE_BM, constants.CHILD_MEM)
        return self.fetchone(query, (util.list_to_sorted_string(child_mem),))

    @util.timeit
    def get_vision_feature_memories(self, channel, kernel):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.CHANNEL, constants.KERNEL)
        return self.fetchall(query, (constants.VISION_FEATURE, channel, kernel))

    @util.timeit
    def get_sound_feature_memories(self, kernel):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? ' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.KERNEL)
        return self.fetchall(query, (constants.SOUND_FEATURE, kernel))

    @util.timeit
    def get_vision_used_kernel(self, kernel):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_VISION_USED_KERNEL, constants.KERNEL)
        return self.fetchone(query, (kernel,))

    @util.timeit
    def get_top_vision_used_kernel(self, offset):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_VISION_USED_KERNEL, constants.COUNT)
        return self.fetchone(query, (offset,))

    @util.timeit
    def insert_vision_used_kernel(self, kernel, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_VISION_USED_KERNEL
        self.execute(query, (kernel, count))

    @util.timeit
    def update_vision_used_kernel(self, kernel, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_VISION_USED_KERNEL, constants.COUNT, constants.KERNEL)
        self.execute(query, (count, kernel))

    @util.timeit
    def clean_vision_used_kernel(self, min_count=3):
        query = 'DELETE FROM %s WHERE %s<?' % (self.TABLE_VISION_USED_KERNEL, constants.COUNT)
        self.execute(query, (min_count,))

    @util.timeit
    def get_sound_used_kernel(self, kernel):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_SOUND_USED_KERNEL, constants.KERNEL)
        return self.fetchone(query, (kernel,))

    @util.timeit
    def get_top_sound_used_kernel(self, offset):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_SOUND_USED_KERNEL, constants.COUNT)
        return self.fetchone(query, (offset,))

    @util.timeit
    def insert_sound_used_kernel(self, kernel, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_SOUND_USED_KERNEL
        self.execute(query, (kernel, count))

    @util.timeit
    def update_sound_used_kernel(self, kernel, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_SOUND_USED_KERNEL, constants.COUNT, constants.KERNEL)
        self.execute(query, (count, kernel))

    @util.timeit
    def clean_sound_used_kernel(self, min_count=3):
        query = 'DELETE FROM %s WHERE %s<?' % (self.TABLE_SOUND_USED_KERNEL, constants.COUNT)
        self.execute(query, (min_count,))

    @util.timeit
    def clean_short_id(self):
        query = 'DELETE FROM {0} WHERE {2} NOT IN (SELECT {2} FROM {1} )'.format(self.TABLE_SHORT_ID, self.TABLE_BM,
                                                                                 constants.MID, )
        self.execute(query)

    @util.timeit
    def get_used_speed(self, speed):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_USED_SPEED, constants.SPEED)
        return self.fetchone(query, (speed,))

    @util.timeit
    def get_top_used_speed(self, offset=0):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_USED_SPEED, constants.COUNT)
        return self.fetchone(query, (offset,))

    @util.timeit
    def insert_used_speed(self, speed, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_USED_SPEED
        self.execute(query, (speed, count))

    @util.timeit
    def update_used_speed(self, speed, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_USED_SPEED, constants.COUNT, constants.SPEED)
        self.execute(query, (count, speed))

    @util.timeit
    def get_used_degrees(self, degrees):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_USED_DEGREES, constants.DEGREES)
        return self.fetchone(query, (degrees,))

    @util.timeit
    def get_top_used_degrees(self, offset=0):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_USED_DEGREES, constants.COUNT)
        return self.fetchone(query, (offset,))

    @util.timeit
    def insert_used_degrees(self, degrees, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_USED_DEGREES
        self.execute(query, (degrees, count))

    @util.timeit
    def update_used_degrees(self, degrees, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_USED_DEGREES, constants.COUNT, constants.DEGREES)
        self.execute(query, (count, degrees))

    @util.timeit
    def get_used_channel(self, channel):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_USED_CHANNEL, constants.CHANNEL)
        return self.fetchone(query, (channel,))

    @util.timeit
    def get_top_used_channel(self, offset=0):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_USED_CHANNEL, constants.COUNT)
        return self.fetchone(query, (offset,))

    @util.timeit
    def insert_used_channel(self, channel, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_USED_CHANNEL
        self.execute(query, (channel, count))

    @util.timeit
    def update_used_channel(self, channel, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_USED_CHANNEL, constants.COUNT, constants.CHANNEL)
        self.execute(query, (count, channel))

    @util.timeit
    def persist(self):
        # need to reset row factory, otherwise there is strange error
        self.con.row_factory = None
        try:
            with open(self.DUMP_FILE, 'w') as f:
                for line in self.con.iterdump():
                    f.write('%s\n' % line)
            logging.info('persisted database')
        except:
            logging.error('failed to persist database')

    @util.timeit
    def import_from_script(self, path):
        logging.info('import_from_script')
        qry = open(path, 'r').read()
        self.connect_db()
        c = self.con.cursor()
        c.executescript(qry)
        self.con.commit()


@util.timeit
def list_many(list1):
    return [(x,) for x in list1]


@util.timeit
def prepare_data(d):
    if constants.CHILD_MEM in d:
        d.update({constants.CHILD_MEM: util.list_to_sorted_string(d.get(constants.CHILD_MEM))})
    if constants.PARENT_MEM in d:
        d.update({constants.PARENT_MEM: util.list_to_str(d.get(constants.PARENT_MEM))})
    if constants.FEATURE in d:
        d.update({constants.FEATURE: util.list_to_str(d.get(constants.FEATURE))})


@util.timeit
def bm_dict_factory(cursor, row):
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
