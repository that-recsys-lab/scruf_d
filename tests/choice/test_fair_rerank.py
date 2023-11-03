import unittest
import toml
from icecream import ic
from collections import defaultdict

from scruf.choice import ChoiceMechanismFactory, FARChoiceMechanism, PFARChoiceMechanism, OFairChoiceMechanism
from scruf.util import ResultList, BallotCollection
from scruf.agent import FairnessAgent, AgentCollection
from scruf.data import CSVContext, ItemFeatureData
from scruf import Scruf

SAMPLE_PROPERTIES1 = '''
[choice]
algorithm = "FAR"
[choice.properties]
binary = "True"
use_allocation_weight = "True"
recommender_weight = 0.8
'''

SAMPLE_PROPERTIES2 = '''
[choice]
algorithm = "PFAR"
[choice.properties]
binary = "True"
use_allocation_weight = "True"
recommender_weight = 0.8
'''

SAMPLE_PROPERTIES3 = '''
[choice]
algorithm = "OFAIR"
[choice.properties]
recommender_weight = 0.8
non_sensitive_discount = 100
epsilon = 0.00000000000000022
alpha = 1.0
'''

# Not testing OFAIR with other than binary features
SAMPLE_FEATURE_CONFIG = '''
[f1]
name = "f1"
protected_feature = true
protected_values = 1

[f2]
name = "f2"
protected_feature = true
protected_values = 1

[f3]
name = "f3"
protected_feature = false 
'''

SAMPLE_COMPATIBILITIES = {'u1': {'f1': 0.8, 'f2': 0.0, 'f3': 0.5},
                          'u2': {'f1': 0.0, 'f2': 0.8, 'f3': 0.5}}

SAMPLE_FEATURES = [('i1', 'f1', 1),
                   ('i1', 'f2', 1),
                   ('i1', 'f3', 1),
                   ('i2', 'f1', 0),
                   ('i2', 'f2', 1),
                   ('i2', 'f3', 1),
                   ('i3', 'f1', 1),
                   ('i3', 'f2', 0),
                   ('i3', 'f3', 1),
                   ('i4', 'f1', 0),
                   ('i4', 'f2', 0),
                   ('i4', 'f3', 1),
                   ('i5', 'f1', 1),
                   ('i5', 'f2', 0),
                   ('i5', 'f3', 0),
                   ]

RESULT_TRIPLES1 = [('u1', 'i5', '5.0'),
                   ('u1', 'i1', '2.5'),
                  ('u1', 'i3', '1.5'),
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

# TODO: Note no test cases for the non-binary version of FAR
class FARTestCase(unittest.TestCase):
    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES1)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        self.assertEqual(choice.__class__, FARChoiceMechanism)
        self.assertAlmostEqual(choice.get_property('recommender_weight'), 0.8)

    def test_FAR(self):
        config = toml.loads(SAMPLE_PROPERTIES1)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])
        self.assertEqual(choice.__class__, FARChoiceMechanism)

        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES3)

        bcoll = BallotCollection()
        bcoll.set_ballot('__rec', rl1, 1.0)
        bcoll.set_ballot('test2', rl2, 1.0)

        output = choice.compute_choice(None, bcoll, rl1, 4)
        self.assertEqual(output.get_length(), 4)
        self.assertEqual('i5', output.results[0].item)
        self.assertEqual('i4', output.results[1].item)

        bcoll2 = BallotCollection()
        bcoll2.set_ballot('__rec', rl1, 1.0)
        bcoll2.set_ballot('test2', rl2, 1.0)
        bcoll2.set_ballot('test3', rl3, 1.0)

        output2 = choice.compute_choice(None, bcoll2, rl1, 4)
        self.assertEqual('i5', output2.results[0].item)
        self.assertEqual('i4', output2.results[1].item)
        self.assertEqual('i2', output2.results[2].item)
        self.assertEqual('i1', output2.results[3].item)

    def test_PFAR(self):
        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        choice.setup(config['choice']['properties'])

        self.assertEqual(choice.__class__, PFARChoiceMechanism)

        scruf = Scruf(None)
        agents = AgentCollection()
        scruf.state.agents = agents

        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES3)

        bcoll2 = BallotCollection()
        bcoll2.set_ballot('__rec', rl1, 1.0)
        bcoll2.set_ballot('test2', rl2, 1.0)
        bcoll2.set_ballot('test3', rl3, 1.0)

        test2agent = FairnessAgent('test2')
        test2agent.recent_compatibility = 0.2
        test3agent = FairnessAgent('test3')
        test3agent.recent_compatibility = 1.0
        agents.agents = [test2agent, test3agent]

        output2 = choice.compute_choice(None, bcoll2, rl1, 4)
        self.assertEqual('i5', output2.results[0].item)
        self.assertEqual('i2', output2.results[1].item)

    def testOFAIR(self):
        config = toml.loads(SAMPLE_PROPERTIES3)
        alg_name = config['choice']['algorithm']
        choice = ChoiceMechanismFactory.create_choice_mechanism(alg_name)

        scruf = Scruf(None)
        agents = AgentCollection()
        scruf.state.agents = agents

        scruf.state.context = CSVContext()
        scruf.state.context.compatibility_dict = SAMPLE_COMPATIBILITIES

        # set up features
        if_index = defaultdict(dict)
        for entry in SAMPLE_FEATURES:
            feature_value = entry[2]
            if_index[entry[0]][entry[1]] = feature_value

        scruf.state.item_features = ItemFeatureData()
        feature_config = toml.loads(SAMPLE_FEATURE_CONFIG)
        scruf.state.item_features.known_features = {}
        scruf.state.item_features.setup_features(feature_config)
        scruf.state.item_features.item_feature_index = if_index
        scruf.state.item_features.setup_indices()

        choice.setup(config['choice']['properties'])

        self.assertEqual(choice.__class__, OFairChoiceMechanism)

        scruf = Scruf(None)
        agents = AgentCollection()
        scruf.state.agents = agents

        scruf.state.context = CSVContext()
        scruf.state.context.compatibility_dict = SAMPLE_COMPATIBILITIES

        # Now we can test

        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)
        rl2 = ResultList()
        rl2.setup(RESULT_TRIPLES2)
        rl3 = ResultList()
        rl3.setup(RESULT_TRIPLES3)

        bcoll = BallotCollection()
        bcoll.set_ballot('__rec', rl1, 0.8)
        bcoll.set_ballot('test2', rl2, 1.0)

        output = choice.compute_choice(None, bcoll, rl1, 4)

        # ic(output)
        self.assertEqual(output.get_length(), 4)
        self.assertEqual('i5', output.results[0].item)
        self.assertEqual('i3', output.results[1].item)


if __name__ == '__main__':
    unittest.main()
