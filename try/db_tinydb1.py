from tinydb import TinyDB, Query

db = TinyDB('TinyDB.json')
table = db.table('Memory')
table.insert({"name": "John", "age": 22})
table.insert({"name": "Grace", "age": 18})
table.insert({"name": "Ben", "age": 22})

User = Query()
print(table.search(User.age == 22))
