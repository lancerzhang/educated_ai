import time, md5
from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex
from CodernityDB.tree_index import TreeBasedIndex
from CodernityDB.database import DatabasePathException


class SimpleTreeIndex(TreeBasedIndex):

    def __init__(self, *args, **kwargs):
        kwargs['node_capacity'] = 13
        kwargs['key_format'] = 'I'
        super(SimpleTreeIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get('z')
        if a_val is not None:
            return a_val, None
        return None

    def make_key(self, key):
        return key


class NameCityIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(NameCityIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        return md5(data.get('name') + data.get('city')).hexdigest(), None

    def make_key(self, key):
        return md5(key.get('name') + key.get('city')).hexdigest()


class NameIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(NameIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        return md5(data['name']).hexdigest(), None

    def make_key(self, key):
        return md5(key).hexdigest()


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


class WithYIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = 'I'
        super(WithYIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get("y")
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
        y_ind = WithYIndex(db.path, 'y')
        name_ind = NameIndex(db.path, 'name')
        z_ind = SimpleTreeIndex(db.path, 'z')
        name_city_ind = NameCityIndex(db.path, 'name_city')
        db.add_index(x_ind)
        db.add_index(y_ind)
        db.add_index(name_ind)
        db.add_index(z_ind)
        db.add_index(name_city_ind)

    record = db.insert({'lrc': 1478892851.771, 'rwd': 0, 'cmy': [],  'pmy': [], 'mid': '773701af1bb745d4a21be7defbfc53f2', 'rcl': 1, 'str': 100, '_id': '773701af1bb745d4a21be7defbfc53f2'})
    record1 = db.get('id', record['_id'])
    print(record1)
    record1.update({'lrc': 1478892851.771})
    db.update(record1)
    record2 = db.get('id', record['_id'])
    print(record2)
    # for x in xrange(100):
    #     db.insert(dict(x=x, y=x + 100, z=x + 200, name='name' + str(x), city='city'))

    # print [x for x in db.all('id')]
    # for curr in db.all('id'):
    #     print curr
    # print db.get('y', 110, with_doc=True)
    # record = db.insert({'_id': '2ebe4506f7034c8ca7ccd97b8e565b6f','name':'name10'})
    # print db.get('name', 'name10', with_doc=True)

    # for curr in db.get_many('z', start=0, end=210, with_doc=True):
    #     print curr
    # print db.get('name_city', {'name': 'name10', 'city': 'city'}, with_doc=True)


if __name__ == '__main__':
    main()
