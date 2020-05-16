import os
import sqlite3
import time

DB_FILE = 'example.db'
DB_BAK = 'bak.db'
SQL_FILE = 'dump.sql'
NUM = 30000

print('%s records' % NUM)

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
if os.path.exists(DB_BAK):
    os.remove(DB_BAK)
if os.path.exists(SQL_FILE):
    os.remove(SQL_FILE)


def list_many(list1):
    return [(x,) for x in list1]


def init_db(path):
    time1 = time.time()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS person
                 (id integer, name text, email text)''')
    conn.commit()
    time2 = time.time()
    print('init db used {0}'.format(time2 - time1))
    for _ in range(NUM):
        cur = c.execute("INSERT INTO person VALUES (1,'apple','apple@test.com')")
        # print cur.lastrowid
        conn.commit()
    conn.close()
    time3 = time.time()
    print('insert records used {0}'.format(time3 - time2))


def init_db_trans(path):
    time1 = time.time()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS person
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, email text)''')
    conn.commit()
    time2 = time.time()
    print('init db used {0}'.format(time2 - time1))
    ids = [(x,) for x in range(NUM)]
    c.executemany("INSERT INTO person VALUES (?,'apple','apple@test.com')", ids)
    conn.commit()
    c.execute('SELECT * FROM person ORDER BY id DESC LIMIT 1 OFFSET 0')
    one = c.fetchone()
    print(one)
    print(one[0])
    c.execute("DELETE FROM person WHERE id=?", (one[0],))
    conn.commit()
    c.execute("INSERT INTO person (name, email) VALUES ('orange','orange@test.com')")
    conn.commit()
    c.execute('SELECT * FROM person ORDER BY id DESC LIMIT 3')
    one = c.fetchall()
    print(one)
    c.executemany("DELETE FROM person WHERE id=?", list_many([1, 2, 3]))
    conn.commit()
    conn.close()
    time3 = time.time()
    print('insert records used {0}'.format(time3 - time2))


def dump_db():
    con = sqlite3.connect(DB_FILE)
    time1 = time.time()
    dumps = con.iterdump()
    con.close
    with open(SQL_FILE, 'w') as f:
        for line in dumps:
            f.write('%s\n' % line)
    con.close()
    time3 = time.time()
    print('write dump used {0}'.format(time3 - time1))


def dump_memory_db():
    qry = open(SQL_FILE, 'r').read()
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.executescript(qry)
    conn.commit()
    time1 = time.time()
    dumps = conn.iterdump()
    with open(SQL_FILE, 'w') as f:
        for line in dumps:
            f.write('%s\n' % line)
    conn.close()
    time3 = time.time()
    print('write dump from memory used {0}'.format(time3 - time1))


def import_db_to_memory():
    start = time.time()
    qry = open(SQL_FILE, 'r').read()
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.executescript(qry)
    conn.commit()
    c.close()
    conn.close()
    end = time.time()
    print('import db to memory used {0}'.format(end - start))


# In performance test, running time of this equals to created a file db, and then bulk insert them.
# So it related to disk performance, if use HDD, it's much slower than iterdump.
def attach_db_to_memory():
    qry = open(SQL_FILE, 'r').read()
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.executescript(qry)
    conn.commit()
    start = time.time()
    c.execute("attach '%s' as __extdb" % DB_BAK)
    c.execute("create table __extdb.%s as select * from %s" % ('person', 'person'))
    c.execute("detach __extdb")
    conn.commit()
    c.close()
    conn.close()
    end = time.time()
    print('attach db used {0}'.format(end - start))


# init_db(DB_FILE)
init_db_trans(DB_FILE)
# init_db(':memory:')
dump_db()
dump_memory_db()
import_db_to_memory()
attach_db_to_memory()
