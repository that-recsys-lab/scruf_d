import unittest
import toml

from scruf.choice import ChoiceMechanismFactory, NullChoiceMechanism, WScoringChoiceMechanism
from scruf.util import Ballot, BallotCollection, ResultList
from icecream import ic

SAMPLE_PROPERTIES = '''
[choice]
algorithm = "null_choice"
'''

SAMPLE_PROPERTIES2 = '''
[choice]
algorithm = "weighted_scoring"
[choice.properties]
recommender_weight = 0.8
'''

class ChoiceMechanismTestCase(unittest.TestCase):

    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)

        self.assertEqual(choice.__class__, NullChoiceMechanism)

        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        self.assertEqual(choice.__class__, WScoringChoiceMechanism)
        self.assertAlmostEqual(choice.get_property('recommender_weight'), 0.8)

    def test_weighted_score(self):
        cmech = WScoringChoiceMechanism()
        config = toml.loads(SAMPLE_PROPERTIES2)
        cmech.setup(config['choice']['properties'])
        ballots = BallotCollection()
        ballot1_triples = [('u1', 'i1', 1.0), ('u1', 'i2', 0.5), ('u1', 'i3', 0.2)]
        ballot1_result = ResultList()
        ballot1_result.setup(ballot1_triples, presorted=True)
        ballots.set_ballot('a1', ballot1_result, 1.0)
        ballot2_triples = [('u1', 'i1', 0.2), ('u1', 'i2', 0.5), ('u1', 'i3', 1.0)]
        ballot2_result = ResultList()
        ballot2_result.setup(ballot2_triples, presorted=False)
        ballots.set_ballot('a2', ballot2_result, 0.5)
        rec_triples = [('u1', 'i1', 0.33), ('u1', 'i2', 0.33), ('u1', 'i3', 0.33)]
        rec_result = ResultList()
        rec_result.setup(rec_triples, presorted=True)

        bcoll, output = cmech.compute_choice([], ballots, rec_result, list_size=3)
        results = output.get_results()
        # i1 = 1.0 * 1.0 + 0.2 * 0.5 + 0.8 * 0.33 = 1.364
        # ic(results)
        self.assertEqual('i1', results[0].item)
        self.assertEqual(1.364, results[0].score)
        # i2 = 0.5 * 1.0 + 0.5 * 0.5 + 0.33 * 0.8 = 1.014
        self.assertEqual('i2', results[1].item)
        self.assertEqual(1.014, results[1].score)
