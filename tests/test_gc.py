import unittest

from mock import patch

from components.mgc import GC


class TestUtil(unittest.TestCase):

    def setUp(self):
        return

    @patch("components.data_adaptor.DataAdaptor")
    def test_gc(self, da):
        gc = GC(da)
        for i in range(0, 60):
            gc.process(0.01)
        da.gc.assert_called()


if __name__ == "__main__":
    unittest.main()
