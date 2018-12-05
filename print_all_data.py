from CodernityDB.database import Database

db = Database('CodernityDB')
db.open()
for x in db.all('id', with_doc=True):
    print x
