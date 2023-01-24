import unittest
import toml

from scruf.choice import ChoiceMechanismFactory, NullChoiceMechanism

SAMPLE_PROPERTIES = '''
[choice]
algorithm = "null_choice"

'''

class ChoiceMechanismTestCase(unittest.TestCase):

    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['choice']['algorithm']
        alloc = ChoiceMechanismFactory.create_choice_mechanism(alg_name)
        #alloc.setup(config['allocation']['properties'])

        self.assertEqual(alloc.__class__, NullChoiceMechanism)
        # self.assertAlmostEqual(alloc.get_property('compatibility_exponent'), 0.7)