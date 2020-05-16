import time

from tinydb import Query
from tinydb import TinyDB

db = TinyDB('db.json')

for x in range(1000):
    db.insert(dict(x=x))

start = time.time()
query = Query()
for x in range(0, 50):
    db.search(query.x == x)
print(time.time() - start)
