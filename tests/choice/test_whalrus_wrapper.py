import unittest
import toml
import whalrus
from icecream import ic

from scruf.choice import ChoiceMechanismFactory, WhalrusWrapperMechanism
from scruf.util import ResultList, BallotCollection

SAMPLE_PROPERTIES1 = '''
[choice]
algorithm = "whalrus"
[choice.properties]
whalrus_rule = "RuleBorda"
recommender_weight = 0.8
'''

RESULT_TRIPLES1 = [('u1', 'i1', '3.5'),
                  ('u1', 'i2', '3.0'),
                  ('u1', 'i3', '2.5'),
                  ('u1', 'i4', '2.0'),
                  ('u1', 'i5', '5.0'),
                  ]

RESULT_TRIPLES2 = [('u2', 'i1', '3.5'),
                  ('u2', 'i2', '3.0'),
                  ('u2', 'i3', '2.5'),
                  ('u2', 'i4', '4.0'),
                  ('u2', 'i5', '5.0'),
                  ]

RESULT_TRIPLES3 = [('u3', 'i4', '3.5'),
                  ('u3', 'i2', '3.0'),
                  ('u3', 'i3', '2.5'),
                  ('u3', 'i1', '4.0'),
                  ('u3', 'i5', '2.0'),
                  ]

class WhalrusWrapperTestCase(unittest.TestCase):

    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES1)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        self.assertEqual(choice.__class__, WhalrusWrapperMechanism)
        self.assertAlmostEqual(choice.get_property('recommender_weight'), 0.8)
        self.assertEqual(choice.whalrus_class.__name__, "RuleBorda")

    def test_convert_ballots(self):
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
        bcoll.set_ballot('test1', rl1, 0.1)
        bcoll.set_ballot('test2', rl2, 0.2)
        bcoll.set_ballot('test3', rl3, 0.3)

        wballots, weights = choice.wrap_ballots(bcoll)

        wballot1 = wballots[0]

        self.assertEqual('i5', wballot1.first())
        self.assertEqual(0.1, weights[0])

        wballot3 = wballots[2]

        self.assertEqual('i1', wballot3.first())
        self.assertEqual(0.3, weights[2])

    def test_apply_rule(self):
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
        bcoll.set_ballot('test1', rl1, 0.1)
        bcoll.set_ballot('test2', rl2, 0.2)
        bcoll.set_ballot('test3', rl3, 0.3)

        wballots, weights = choice.wrap_ballots(bcoll)

        choice.invoke_whalrus_rule(wballots, weights)

        self.assertEqual('i1', choice.whalrus_rule.winner_)

        result = choice.whalrus_rule.scores_as_floats_

        self.assertAlmostEqual(3.1667, result['i1'], 4)

    def test_unwrap_results(self):
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
        bcoll.set_ballot('test1', rl1, 0.1)
        bcoll.set_ballot('test2', rl2, 0.2)
        bcoll.set_ballot('test3', rl3, 0.3)

        wballots, weights = choice.wrap_ballots(bcoll)

        choice.invoke_whalrus_rule(wballots, weights)

        result: ResultList = choice.unwrap_result('foo', 2)

        result_contents = result.get_results()

        self.assertEqual(2, len(result_contents))
        top_result = result_contents[0]
        self.assertEqual('foo', top_result.user)
        self.assertEqual('i1', top_result.item)
        self.assertAlmostEqual(3.1667, top_result.score, 4)

        second_result = result_contents[1]
        self.assertEqual('foo', second_result.user)
        self.assertEqual('i4', second_result.item)
        self.assertAlmostEqual(2.5, second_result.score, 4)
