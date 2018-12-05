import time
from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex
from CodernityDB.database import DatabasePathException


class WithXIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = 'I'
        super(WithXIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get("x")
        if a_val is not None:
            return a_val, None
        return None

    def make_key(self, key):
        return key


def main():
    db = Database('CodernityDB')
    try:
        db.open()
    except DatabasePathException:
        db.create()
        x_ind = WithXIndex(db.path, 'x')
        db.add_index(x_ind)
    new_record=db.insert(dict(x=1000))
    record1 = db.get('x', 1001, with_doc=True).get('doc')
    print record1
    # record1.update({'x': 1001})
    # db.update(record1)
    db.delete(record1)
    # db.compact()
    record1 = db.get('x', 1001, with_doc=True)
    print record1


if __name__ == '__main__':
    main()
