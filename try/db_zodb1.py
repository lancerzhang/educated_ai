import ZODB, ZODB.FileStorage
storage = ZODB.FileStorage.FileStorage('ZODB.fs')
db = ZODB.DB(storage)
connection = db.open()
#root = connection.root
#root.acct="account"
print(connection.get("acct"))