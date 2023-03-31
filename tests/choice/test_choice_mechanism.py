import unittest
import toml

from scruf.choice import ChoiceMechanismFactory, NullChoiceMechanism, WScoringChoiceMechanism

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
