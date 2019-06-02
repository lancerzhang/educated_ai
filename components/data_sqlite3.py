import constants
import logging
import os
import sqlite3
import util


class DataSqlite3:
    con = None
    DUMP_FILE = ''
    TABLE_BM = 'bm'
    TABLE_VISION_USED_KERNEL = 'vuk'
    TABLE_SOUND_USED_KERNEL = 'suk'
    TABLE_USED_SPEED = 'spd'
    TABLE_USED_DEGREES = 'dgr'
    TABLE_USED_CHANNEL = 'cnl'

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
        self.con.commit()

    def __init__(self, path):
        self.DUMP_FILE = path
        if os.path.exists(path):
            self.import_from_script(path)
        else:
            self.con = sqlite3.connect(':memory:')
            self.create_tables()

    def insert(self, bm):
        columns = ', '.join(bm.keys())
        placeholders = ':' + ', :'.join(bm.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (self.TABLE_BM, columns, placeholders)
        prepare_data(bm)
        c = self.con.cursor()
        c.execute(query, bm)
        self.con.commit()

    def get_by_id(self, eid):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_BM, constants.MID)
        c = self.con.cursor()
        c.execute(query, (eid,))
        return c.fetchone()

    def get_all(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s ' % self.TABLE_BM
        c = self.con.cursor()
        c.execute(query)
        return c.fetchall()

    def update(self, content, mid):
        params = [key + "=:" + key for key in content]
        updates = ', '.join(params)
        query = 'UPDATE {0} SET {1} WHERE {2}=:{2}'.format(self.TABLE_BM, updates, constants.MID)
        prepare_data(content)
        content.update({constants.MID: mid})
        c = self.con.cursor()
        c.execute(query, content)
        self.con.commit()

    def remove(self, eid):
        query = 'DELETE FROM %s WHERE %s=?' % (self.TABLE_BM, constants.MID)
        c = self.con.cursor()
        c.execute(query, (eid,))
        self.con.commit()

    def search_by_last_call(self, last_call):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_BM, constants.LAST_RECALL_TIME)
        c = self.con.cursor()
        c.execute(query, (last_call,))
        return c.fetchall()

    def get_eden_memories(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_BM, constants.RECALL_COUNT)
        c = self.con.cursor()
        c.execute(query, (2,))
        return c.fetchall()

    def get_young_memories(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM {0} WHERE {1}>=? AND {1}<? '.format(self.TABLE_BM, constants.RECALL_COUNT)
        c = self.con.cursor()
        c.execute(query, (2, 20))
        return c.fetchall()

    def get_old_memories(self):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s>=?  ' % (self.TABLE_BM, constants.RECALL_COUNT)
        c = self.con.cursor()
        c.execute(query, (20,))
        return c.fetchall()

    def get_vision_move_memory(self, degrees, speed, duration):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.DEGREES, constants.SPEED,
            constants.MOVE_DURATION)
        c = self.con.cursor()
        c.execute(query, (constants.VISION_FOCUS_MOVE, degrees, speed, duration))
        return c.fetchone()

    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.ZOOM_TYPE, constants.ZOOM_DIRECTION)
        c = self.con.cursor()
        c.execute(query, (constants.VISION_FOCUS_ZOOM, zoom_type, zoom_direction))
        return c.fetchone()

    def get_mouse_click_memory(self, click_type):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.CLICK_TYPE)
        c = self.con.cursor()
        c.execute(query, (constants.ACTION_MOUSE_CLICK, click_type))
        return c.fetchone()

    def get_by_child_ids(self, child_mem):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? ' % (self.TABLE_BM, constants.CHILD_MEM)
        c = self.con.cursor().execute(query, (util.list_to_sorted_string(child_mem),))
        return c.fetchone()

    def get_vision_feature_memories(self, channel, kernel):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=?' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.CHANNEL, constants.KERNEL)
        c = self.con.cursor().execute(query, (constants.VISION_FEATURE, channel, kernel))
        return c.fetchall()

    def get_sound_feature_memories(self, kernel):
        self.con.row_factory = bm_dict_factory
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? ' % (
            self.TABLE_BM, constants.PHYSICAL_MEMORY_TYPE, constants.KERNEL)
        c = self.con.cursor().execute(query, (constants.SOUND_FEATURE, kernel))
        return c.fetchall()

    def get_vision_used_kernel(self, kernel):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_VISION_USED_KERNEL, constants.KERNEL)
        c = self.con.cursor().execute(query, (kernel,))
        record = c.fetchone()
        return record

    def get_top_vision_used_kernel(self, offset):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_VISION_USED_KERNEL, constants.COUNT)
        c = self.con.cursor().execute(query, (offset,))
        record = c.fetchone()
        return record

    def insert_vision_used_kernel(self, kernel, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_VISION_USED_KERNEL
        c = self.con.cursor()
        c.execute(query, (kernel, count))
        self.con.commit()

    def update_vision_used_kernel(self, kernel, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_VISION_USED_KERNEL, constants.COUNT, constants.KERNEL)
        c = self.con.cursor()
        c.execute(query, (count, kernel))
        self.con.commit()

    def clean_vision_used_kernel(self, min_count=3):
        query = 'DELETE FROM %s WHERE %s<?' % (self.TABLE_VISION_USED_KERNEL, constants.COUNT)
        c = self.con.cursor()
        c.execute(query, (min_count,))
        self.con.commit()

    def get_sound_used_kernel(self, kernel):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_SOUND_USED_KERNEL, constants.KERNEL)
        c = self.con.cursor().execute(query, (kernel,))
        record = c.fetchone()
        return record

    def get_top_sound_used_kernel(self, offset):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_SOUND_USED_KERNEL, constants.COUNT)
        c = self.con.cursor().execute(query, (offset,))
        record = c.fetchone()
        return record

    def insert_sound_used_kernel(self, kernel, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_SOUND_USED_KERNEL
        c = self.con.cursor()
        c.execute(query, (kernel, count))
        self.con.commit()

    def update_sound_used_kernel(self, kernel, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_SOUND_USED_KERNEL, constants.COUNT, constants.KERNEL)
        c = self.con.cursor()
        c.execute(query, (count, kernel))
        self.con.commit()

    def clean_sound_used_kernel(self, min_count=3):
        query = 'DELETE FROM %s WHERE %s<?' % (self.TABLE_SOUND_USED_KERNEL, constants.COUNT)
        c = self.con.cursor()
        c.execute(query, (min_count,))
        self.con.commit()

    def get_used_speed(self, speed):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_USED_SPEED, constants.SPEED)
        c = self.con.cursor().execute(query, (speed,))
        record = c.fetchone()
        return record

    def get_top_used_speed(self, offset=0):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_USED_SPEED, constants.COUNT)
        c = self.con.cursor().execute(query, (offset,))
        record = c.fetchone()
        return record

    def insert_used_speed(self, speed, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_USED_SPEED
        c = self.con.cursor()
        c.execute(query, (speed, count))
        self.con.commit()

    def update_used_speed(self, speed, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_USED_SPEED, constants.COUNT, constants.SPEED)
        c = self.con.cursor()
        c.execute(query, (count, speed))
        self.con.commit()

    def get_used_degrees(self, degrees):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_USED_DEGREES, constants.DEGREES)
        c = self.con.cursor().execute(query, (degrees,))
        record = c.fetchone()
        return record

    def get_top_used_degrees(self, offset=0):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_USED_DEGREES, constants.COUNT)
        c = self.con.cursor().execute(query, (offset,))
        record = c.fetchone()
        return record

    def insert_used_degrees(self, degrees, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_USED_DEGREES
        c = self.con.cursor()
        c.execute(query, (degrees, count))
        self.con.commit()

    def update_used_degrees(self, degrees, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_USED_DEGREES, constants.COUNT, constants.DEGREES)
        c = self.con.cursor()
        c.execute(query, (count, degrees))
        self.con.commit()

    def get_used_channel(self, channel):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_USED_CHANNEL, constants.CHANNEL)
        c = self.con.cursor().execute(query, (channel,))
        record = c.fetchone()
        return record

    def get_top_used_channel(self, offset=0):
        self.con.row_factory = sqlite3.Row
        query = 'SELECT * FROM %s ORDER BY %s DESC LIMIT 1 OFFSET ?' % (self.TABLE_USED_CHANNEL, constants.COUNT)
        c = self.con.cursor().execute(query, (offset,))
        record = c.fetchone()
        return record

    def insert_used_channel(self, channel, count=1):
        query = 'INSERT INTO %s VALUES (?,?)' % self.TABLE_USED_CHANNEL
        c = self.con.cursor()
        c.execute(query, (channel, count))
        self.con.commit()

    def update_used_channel(self, channel, count):
        query = 'UPDATE %s SET %s=? WHERE %s=?' % (self.TABLE_USED_CHANNEL, constants.COUNT, constants.CHANNEL)
        c = self.con.cursor()
        c.execute(query, (count, channel))
        self.con.commit()

    def persist(self):
        # need to reset row factory, otherwise there is strange error
        self.con.row_factory = None
        with open(self.DUMP_FILE, 'w') as f:
            for line in self.con.iterdump():
                f.write('%s\n' % line)
        logging.info('persisted database')

    def import_from_script(self, path):
        qry = open(path, 'r').read()
        self.con = sqlite3.connect(':memory:')
        c = self.con.cursor()
        c.executescript(qry)
        self.con.commit()


def prepare_data(d):
    if constants.CHILD_MEM in d:
        d.update({constants.CHILD_MEM: util.list_to_sorted_string(d.get(constants.CHILD_MEM))})
    if constants.PARENT_MEM in d:
        d.update({constants.PARENT_MEM: util.list_to_str(d.get(constants.PARENT_MEM))})
    if constants.FEATURE in d:
        d.update({constants.FEATURE: util.list_to_str(d.get(constants.FEATURE))})


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
