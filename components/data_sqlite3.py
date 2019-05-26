import constants
import logging
import os
import sqlite3
import util


class DataSqlite3:
    con = None
    TABLE_NAME = 'bm'
    DUMP_FILE = ''

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
        self.con.commit()

    def __init__(self, path):
        self.DUMP_FILE = path
        if os.path.exists(path):
            self.import_from_script(path)
        else:
            self.con = sqlite3.connect(':memory:')
            self.create_tables()
        self.con.row_factory = dict_factory

    def insert(self, bm):
        columns = ', '.join(bm.keys())
        placeholders = ':' + ', :'.join(bm.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (self.TABLE_NAME, columns, placeholders)
        prepare_data(bm)
        c = self.con.cursor()
        c.execute(query, bm)
        self.con.commit()

    def get_by_id(self, eid):
        query = 'SELECT * FROM %s WHERE %s=?' % (self.TABLE_NAME, constants.MID)
        c = self.con.cursor()
        c.execute(query, (eid,))
        return c.fetchone()

    def get_all(self):
        query = 'SELECT * FROM %s ' % self.TABLE_NAME
        c = self.con.cursor()
        c.execute(query)
        return c.fetchall()

    def update(self, content, mid):
        params = [key + "=:" + key for key in content]
        updates = ', '.join(params)
        query = 'UPDATE {0} SET {1} WHERE {2}=:{2}'.format(self.TABLE_NAME, updates, constants.MID)
        prepare_data(content)
        content.update({constants.MID: mid})
        c = self.con.cursor()
        c.execute(query, content)
        self.con.commit()

    def remove(self, eid):
        query = 'DELETE FROM %s WHERE %s=?' % (self.TABLE_NAME, constants.MID)
        c = self.con.cursor()
        c.execute(query, (eid,))
        self.con.commit()

    def search_by_last_call(self, last_call):
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_NAME, constants.LAST_RECALL_TIME)
        c = self.con.cursor()
        c.execute(query, (last_call,))
        return c.fetchall()

    def get_eden_memories(self):
        query = 'SELECT * FROM %s WHERE %s<? ' % (self.TABLE_NAME, constants.RECALL_COUNT)
        c = self.con.cursor()
        c.execute(query, (2,))
        return c.fetchall()

    def get_young_memories(self):
        query = 'SELECT * FROM {0} WHERE {1}>=? AND {1}<? '.format(self.TABLE_NAME, constants.RECALL_COUNT)
        c = self.con.cursor()
        c.execute(query, (2, 20))
        return c.fetchall()

    def get_old_memories(self):
        query = 'SELECT * FROM %s WHERE %s>=?  ' % (self.TABLE_NAME, constants.RECALL_COUNT)
        c = self.con.cursor()
        c.execute(query, (20,))
        return c.fetchall()

    def get_vision_move_memory(self, degrees, speed, duration):
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=? AND %s=?' % (
            self.TABLE_NAME, constants.PHYSICAL_MEMORY_TYPE, constants.DEGREES, constants.SPEED,
            constants.MOVE_DURATION)
        c = self.con.cursor()
        c.execute(query, (constants.VISION_FOCUS_MOVE, degrees, speed, duration))
        return c.fetchone()

    def get_vision_zoom_memory(self, zoom_type, zoom_direction):
        query = 'SELECT * FROM %s WHERE %s=? AND %s=? AND %s=?' % (
            self.TABLE_NAME, constants.PHYSICAL_MEMORY_TYPE, constants.ZOOM_TYPE, constants.ZOOM_DIRECTION)
        c = self.con.cursor()
        c.execute(query, (constants.VISION_FOCUS_ZOOM, zoom_type, zoom_direction))
        return c.fetchone()

    def get_mouse_click_memory(self, click_type):
        query = 'SELECT * FROM %s WHERE %s=? AND %s=?' % (
            self.TABLE_NAME, constants.PHYSICAL_MEMORY_TYPE, constants.CLICK_TYPE)
        c = self.con.cursor()
        c.execute(query, (constants.ACTION_MOUSE_CLICK, click_type))
        return c.fetchone()

    def get_by_child_ids(self, child_mem):
        query = 'SELECT * FROM %s WHERE %s=? ' % (self.TABLE_NAME, constants.CHILD_MEM)
        c = self.con.cursor().execute(query, (util.list_to_sorted_string(child_mem),))
        return c.fetchone()

    def persist(self):
        self.con.row_factory = None
        with open(self.DUMP_FILE, 'w') as f:
            for line in self.con.iterdump():
                f.write('%s\n' % line)
        self.con.row_factory = dict_factory
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
