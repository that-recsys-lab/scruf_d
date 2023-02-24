import unittest
from scruf.util import normalize_score_dict, collapse_score_dict
from random import Random


class ScoreDictTestCase(unittest.TestCase):
    def test_normalize(self):
        d1 = {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd':0.0}

        d2 = normalize_score_dict(d1, inplace=False)

        self.assertTrue(all([score == 0.0 for label, score in d2.items()]))

        d3 = {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd':1.0}
        normalize_score_dict(d3, inplace=True)

        self.assertTrue(all([score == 0.25 for label, score in d3.items()]))

    def test_collapse(self):
        d1 = {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd':0.0}
        val = collapse_score_dict(d1, type='max', handle_multiple='first')
        self.assertIsNone(val)

        d2 = {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd': 1.0}
        val = collapse_score_dict(d2, type='min', handle_multiple='first')
        self.assertIsNone(val)

        d3 = {'a': 1.0, 'b': 0.5, 'c': 0.5, 'd': 1.0}
        val = collapse_score_dict(d3, type='max', handle_multiple='first')
        self.assertEqual(val, 'a')

        val = collapse_score_dict(d3, type='min', handle_multiple='first')
        self.assertEqual(val, 'b')

        rand = Random(20220223)
        val = collapse_score_dict(d3, type='max', handle_multiple='random', rand=rand)
        self.assertEqual(val, 'd')


if __name__ == '__main__':
    unittest.main()
