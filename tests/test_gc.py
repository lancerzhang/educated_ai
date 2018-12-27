from mgc import GC
from mock import patch, Mock, MagicMock
import constants
import unittest
import numpy as np


class TestUtil(unittest.TestCase):

    def setUp(self):
        return

    @patch("data_adaptor.DataAdaptor")
    def test_gc(self, da):
        gc = GC(da)
        for i in range(0, 60):
            gc.process(0.01)
        da.gc.assert_called()


if __name__ == "__main__":
    unittest.main()
