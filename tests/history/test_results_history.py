import unittest
from icecream import ic
from scruf.history import ResultsHistory
from scruf.util import ResultList

RESULT_TRIPLES_1 = [('u1', 'i1', '3.5'),
                  ('u1', 'i2', '3.0'),
                  ('u1', 'i3', '2.5'),
                  ('u1', 'i4', '4.0'),
                  ('u1', 'i5', '5.0'),
                  ]

RESULT_TRIPLES_2 = [('u2', 'i11', '3.5'),
                  ('u2', 'i12', '3.0'),
                  ('u2', 'i3', '2.5'),
                  ('u2', 'i14', '4.0'),
                  ('u2', 'i5', '5.0'),
                  ]

RESULT_TRIPLES_3 = [('u3', 'i21', '3.5'),
                  ('u3', 'i12', '3.0'),
                  ('u3', 'i3', '2.5'),
                  ('u3', 'i24', '4.0'),
                  ('u3', 'i25', '5.0'),
                  ]

class TestResultsHistory(unittest.TestCase):

    def setUp(self):
        self.rlist1 = ResultList()
        self.rlist2 = ResultList()
        self.rlist3 = ResultList()

        self.rlist1.setup(RESULT_TRIPLES_1)
        self.rlist2.setup(RESULT_TRIPLES_2)
        self.rlist3.setup(RESULT_TRIPLES_3)

    def test_rhist_create(self):
        rhist = ResultsHistory(5)
        rhist.add_items([self.rlist3, self.rlist2, self.rlist1])

        rhist.add_items([self.rlist3, self.rlist2, self.rlist1]) # last one should get dropped

        result_lists = rhist.get_recent_results(-1)
        self.assertEqual(len(result_lists), 25)

    def test_rhist_output(self):
        rhist = ResultsHistory(5)
        rhist.add_items([self.rlist3, self.rlist2, self.rlist1])

        result_entries = rhist.get_recent_results(3)
        self.assertEqual(len(result_entries), 15)
        self.assertEqual(result_entries[0].user, 'u1')
        self.assertEqual(result_entries[0].item, 'i5')
        self.assertEqual(result_entries[14].user, 'u3')

        item_counts = rhist.get_item_counts(3)
        self.assertEqual(item_counts['i1'], 1)
        self.assertEqual(item_counts['i3'], 3)
        self.assertEqual(item_counts['i12'], 2)
        self.assertEqual(item_counts['i25'], 1)


if __name__ == '__main__':
    unittest.main()
