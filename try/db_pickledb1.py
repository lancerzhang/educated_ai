import msvcrt
import pickledb
db = pickledb.load('pickledb.db', False)
value= db.get('key')
if value is None:value=0
print("existing value is:",value)
db.set('key', value+1)
print("new value is:",db.get('key'))

try:
    while 1:
        a=1

except KeyboardInterrupt:
        print("begin to dump.")
        db.dump()