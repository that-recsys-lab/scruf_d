import unittest
import toml
from icecream import ic

from scruf.choice import ChoiceMechanismFactory, xQuadChoiceMechanism
from scruf.util import ResultList, BallotCollection

SAMPLE_PROPERTIES1 = '''
[choice]
algorithm = "xquad"
[choice.properties]
recommender_weight = 0.8
'''

SAMPLE_PROPERTIES2 = '''
[choice]
algorithm = "mmr_sum"
[choice.properties]
recommender_weight = 0.8
'''

SAMPLE_PROPERTIES3 = '''
[choice]
algorithm = "mmr_max"
[choice.properties]
recommender_weight = 0.8
'''


RESULT_TRIPLES1 = [('u1', 'i5', '5.0'),
                   ('u1', 'i1', '3.5'),
                  ('u1', 'i3', '2.5'),
                  ('u1', 'i4', '2.0'),
                   ('u1', 'i2', '1.7')
                  ]

RESULT_TRIPLES2 = [('u1', 'i4', '1.0'),
                  ('u1', 'i2', '1.0'),
                  ('u1', 'i3', '0.0'),
                  ('u1', 'i1', '0.0'),
                  ('u1', 'i5', '0.0'),
                  ]

RESULT_TRIPLES3 = [('u1', 'i4', '0.0'),
                  ('u1', 'i2', '0.4'),
                  ('u1', 'i3', '0.4'),
                  ('u1', 'i1', '0.0'),
                  ('u1', 'i5', '0.0'),
                  ]

RESULT_TRIPLES4 = [('u1', 'i4', '0.4'),
                  ('u1', 'i2', '0.4'),
                  ('u1', 'i3', '0.4'),
                  ('u1', 'i1', '0.0'),
                  ('u1', 'i5', '0.0'),
                  ]


class GreedySublistTestCase(unittest.TestCase):
    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES1)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        self.assertEqual(choice.__class__, xQuadChoiceMechanism)
        self.assertAlmostEqual(choice.get_property('recommender_weight'), 0.8)

    def test_rerank(self):
        config = toml.loads(SAMPLE_PROPERTIES1)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES3)

        bcoll = BallotCollection()
        bcoll.set_ballot('__rec', rl1, 1.0)
        bcoll.set_ballot('test2', rl2, 1.0)

        _, result_lst = choice.compute_choice(None, bcoll, rl1, 4)
        self.assertEqual(result_lst.get_length(), 4)
        self.assertEqual('i5', result_lst.results[0].item)
        self.assertEqual('i4', result_lst.results[2].item)

        bcoll2 = BallotCollection()
        bcoll2.set_ballot('__rec', rl1, 1.0)
        bcoll2.set_ballot('test3', rl3, 1.0)

        _, result_lst2 = choice.compute_choice(None, bcoll2, rl1, 4)
        self.assertEqual('i5', result_lst2.results[0].item)
        self.assertEqual('i1', result_lst2.results[1].item)
        self.assertEqual('i3', result_lst2.results[2].item)
        self.assertEqual('i2', result_lst2.results[3].item)

    def test_mmr(self):
        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES4)

        bcoll = BallotCollection()
        bcoll.set_ballot('__rec', rl1, 0.8)
        bcoll.set_ballot('test2', rl2, 1.0) # allocations are ignored
        bcoll.set_ballot('test3', rl3, 1.0)

        ballots, result_lst = choice.compute_choice(None, bcoll, rl1, 4)
        self.assertEqual(result_lst.get_length(), 4)
        self.assertEqual('i5', result_lst.results[0].item)
        self.assertEqual('i3', result_lst.results[2].item)

    def test_mmr_max(self):
        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES4)

        bcoll = BallotCollection()
        bcoll.set_ballot('__rec', rl1, 0.8)
        bcoll.set_ballot('test2', rl2, 1.0) # allocations are ignored
        bcoll.set_ballot('test3', rl3, 1.0)

        _, result_lst = choice.compute_choice(None, bcoll, rl1, 4)
        self.assertEqual(result_lst.get_length(), 4)
        self.assertEqual('i5', result_lst.results[0].item)
        self.assertEqual('i3', result_lst.results[2].item)

if __name__ == '__main__':
    unittest.main()
