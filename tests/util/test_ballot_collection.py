import unittest

from scruf.util import ResultList, Ballot, BallotCollection

RESULT_TRIPLES1 = [('u1', 'i1', '3.5'),
                  ('u1', 'i2', '3.0'),
                  ('u1', 'i3', '2.5'),
                  ('u1', 'i4', '4.0'),
                  ('u1', 'i5', '5.0'),
                  ]

RESULT_TRIPLES2 = [('u2', 'i1', '3.5'),
                  ('u2', 'i2', '3.0'),
                  ('u2', 'i3', '2.5'),
                  ('u2', 'i4', '4.0'),
                  ('u2', 'i5', '5.0'),
                  ]

RESULT_TRIPLES3 = [('u3', 'i1', '3.5'),
                  ('u3', 'i2', '3.0'),
                  ('u3', 'i3', '2.5'),
                  ('u3', 'i4', '4.0'),
                  ('u3', 'i5', '5.0'),
                  ]


class TestBallotCollection(unittest.TestCase):
    def test_ballot(self):
        rl = ResultList()
        rl.setup(RESULT_TRIPLES1)
        bal = Ballot('test', rl)
        self.assertEqual('test', bal.name)
        self.assertEqual(1.0, bal.weight)
        prefs = bal.prefs.get_results()
        self.assertEqual('i5', prefs[0].item)

        bal = Ballot('test', rl, 0.5)
        self.assertEqual(0.5, bal.weight)

    def test_bcollection(self):
        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES3)

        bcoll = BallotCollection()
        bcoll.set_ballot('test1', rl1, 0.1)
        bcoll.set_ballot('test2', rl2, 0.2)
        bcoll.set_ballot('test3', rl3, 0.3)

        self.assertEqual(0.2, bcoll.get_weights()['test2'])
        self.assertEqual('u3', bcoll.get_ballot('test3').prefs.get_user())


if __name__ == '__main__':
    unittest.main()
