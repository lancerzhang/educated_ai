import time
from CodernityDB.database import Database
from CodernityDB.tree_index import TreeBasedIndex
from CodernityDB.database import DatabasePathException


class SimpleTreeIndex(TreeBasedIndex):

    def __init__(self, *args, **kwargs):
        kwargs['node_capacity'] = 13
        kwargs['key_format'] = 'I'
        super(SimpleTreeIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get('lrc')
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
        x_ind = SimpleTreeIndex(db.path, 'lrc')
        db.add_index(x_ind)

    # for x in xrange(2):
    #     db.insert({'lrc': x, 'rwd': 0, 'cmy': [],  'pmy': [], 'rcl': 1, 'str': 100})
    db.insert({'lrc': 1, 'rwd': 0, 'cmy': [], 'pmy': [],  'rcl': 1, 'str': 100})
    db.insert({'lrc': 2, 'rwd': 0, 'cmy': [], 'pmy': [],  'rcl': 1, 'str': 100})
    # for i in db.all('id'):
    #     print i
    multi_records = db.get_many('lrc',  end=100, with_doc=True)
    for curr in multi_records:
        print curr


if __name__ == '__main__':
    main()
