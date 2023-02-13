import unittest
from icecream import ic

from scruf.util import ResultList

RESULT_TRIPLES = [('u1', 'i1', '3.5'),
                  ('u1', 'i2', '3.0'),
                  ('u1', 'i3', '2.5'),
                  ('u1', 'i4', '4.0'),
                  ('u1', 'i5', '5.0'),
                  ]

class ResultListTestCase(unittest.TestCase):
    def test_result_list_create(self):

        rlist = ResultList()
        rlist.setup(RESULT_TRIPLES, presorted=True)
        self.assertEqual(rlist.get_results()[4].item, 'i5')  # If it doesn't sort, i5 will still be last

        rlist.setup(RESULT_TRIPLES, presorted=False)
        self.assertEqual(rlist.get_results()[4].item, 'i3')  # If it sorts, i3 will still be last

        rlist.setup(RESULT_TRIPLES, presorted=False, trim=3)
        self.assertEqual(len(rlist.get_results()), 3)

    def test_rescore(self):
        rlist = ResultList()
        rlist.setup(RESULT_TRIPLES)
        # Reverses the order
        rlist.rescore(lambda result: -2.0 * result.score)
        res = rlist.get_results()[0]
        self.assertEqual(res.item, 'i3')
        self.assertEqual(res.score, -5.0)
        self.assertEqual(res.rank, 0)

    def test_filter(self):
        rlist = ResultList()
        rlist.setup(RESULT_TRIPLES)
        filtered = list(rlist.filter_results(lambda result: result.score > 3.5))
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].item, 'i5')

    def test_combine(self):
        rlist1 = ResultList()
        rlist1.setup(RESULT_TRIPLES)
        rlist2 = ResultList()
        rlist2.setup(RESULT_TRIPLES)
        output = ResultList.combine_results([rlist1, rlist2])

        self.assertEqual(output.results[0].item, 'i5')
        self.assertEqual(output.results[0].score, 10)

if __name__ == '__main__':
    unittest.main()
