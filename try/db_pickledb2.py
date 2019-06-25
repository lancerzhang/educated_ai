import msvcrt
import pickledb
db = pickledb.load('pickledb.db', False)
db.lcreate("100")
db.ladd("100",{"name":"Grace"})
db.ladd("100",{"name":"John"})
db.lcreate("99")
db.ladd("99",{"name":"Ben"})
db.ladd("99",{"name":"Ken"})
print(db.lgetall("100"))
db.dump()