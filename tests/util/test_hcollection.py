import unittest
from scruf.util import HistoryCollection


class TestHistoryCollection(unittest.TestCase):
    def test_hc_creation(self):

        hc = HistoryCollection()
        hc.add_items(['a', 'b', 'c', 'd', 'e'])

        self.assertEqual(len(hc.collection), 5)
        self.assertEqual(hc.time, 5)

    def test_hc_access(self):

        hc = HistoryCollection()
        hc.add_items(['a', 'b', 'c', 'd', 'e'])

        recent = hc.get_recent(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0], 'e')

        self.assertEqual(hc.get_from_time(3), 'd')


if __name__ == '__main__':
    unittest.main()
