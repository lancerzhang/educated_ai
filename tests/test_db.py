import unittest, sound, memory
from db import Database
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))


    def test_get_memory(self):
        elid = self.database._add_memory()
        record = self.database._get_memory(elid)
        self.assertEqual(record[memory.TYPE], memory.MEMORY)

    def test_add_memory(self):
        self.database._add_memory()
        query = Query()
        record = self.database.table.search(query[memory.TYPE] == memory.MEMORY)[0]
        self.assertEqual(record[memory.TYPE], memory.MEMORY)
        self.assertGreater(record[memory.LASTRECALL], 0)

    def test_add_vision(self):
        self.database._add_vision()
        query = Query()
        record = self.database.table.search(query[memory.TYPE] == memory.VISION)[0]
        self.assertEqual(record[memory.TYPE], memory.VISION)
        self.assertGreater(record[memory.LASTRECALL], 0)

    def test_add_sound(self):
        self.database._add_sound()
        query = Query()
        record = self.database.table.search(query[memory.TYPE] == memory.SOUND)[0]
        self.assertEqual(record[memory.TYPE], memory.SOUND)
        self.assertGreater(record[memory.LASTRECALL], 0)

    def test_add_focus(self):
        self.database._add_focus()
        query = Query()
        record = self.database.table.search(query[memory.TYPE] == memory.FOCUS)[0]
        self.assertEqual(record[memory.TYPE], memory.FOCUS)
        self.assertGreater(record[memory.LASTRECALL], 0)

    def test_add_speak(self):
        self.database._add_speak()
        query = Query()
        record = self.database.table.search(query[memory.TYPE] == memory.SPEAK)[0]
        self.assertEqual(record[memory.TYPE], memory.SPEAK)
        self.assertGreater(record[memory.LASTRECALL], 0)

    def test_search_sound(self):
        self.database._add_sound({sound.FEATURE: 1, sound.INDEX: 100})
        self.database._add_sound({sound.FEATURE: 1, sound.ENERGY: 5000})
        records = self.database._search_sound(1, sound.INDEX, 1, 1)
        self.assertEqual(0, len(records))
        records = self.database._search_sound(1, sound.INDEX, 120, 120)
        self.assertEqual(0, len(records))
        records = self.database._search_sound(1, sound.INDEX, 80, 120)
        self.assertEqual(1, len(records))
        records = self.database._search_sound(1, sound.ENERGY, 1000, 1000)
        self.assertEqual(0, len(records))
        records = self.database._search_sound(1, sound.ENERGY, 6000, 6000)
        self.assertEqual(0, len(records))
        records = self.database._search_sound(1, sound.ENERGY, 4500, 5500)
        self.assertEqual(1, len(records))

if __name__ == "__main__":
    unittest.main()
