import unittest
import toml
import tempfile
import pathlib


from scruf.agent import CompatibilityMetricFactory, FairnessAgent, ContextCompatibilityMetric
from scruf.util import PropertyMismatchError, UnregisteredCompatibilityMetricError, \
    InvalidCompatibilityMetricError
from scruf.data import CSVContext


TEST_COMPATIBILITIES_FILE = 'compat_data.csv'

SAMPLE_COMPATIBILITIES = '''user1,agent1,1.0
user1,agent2,0.5
user1,agent3,0.0
user2,agent1,0.55
user2,agent2,0.75
user2,agent3,0.95
'''

CONFIG_DOCUMENT="""
[location]
path = "your_path/here"
overwrite = "true"

[context]
context_class = "csv_context"

[context.properties]
compatibility_file = "compat_data.csv"

[feature]

[feature.one]
name = "COUNTRY_low_pfr"
protected_feature = "COUNTRY_low_pfr"
protected_values = [1]

[agent]

[agent.country]
name = "country"
metric_class = "proportional_item"
compatibility_class = "context_compatibility"
preference_function_class = "binary_preference"

[agent.country.metric]
feature = "COUNTRY_low_pfr"
proportion = 0.2

[agent.country.preference]
delta = 0.3
feature = "COUNTRY_low_pfr"
"""

class ContextCompatibilityTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)
        with open(self.temp_dir_path / TEST_COMPATIBILITIES_FILE, 'w') as feature_file:
            feature_file.write(SAMPLE_COMPATIBILITIES)

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.temp_dir.cleanup()

    def test_context_compatibility(self):
        config = toml.loads(CONFIG_DOCUMENT)
        config_agent = config['agent']['country']

        agent = FairnessAgent(config_agent['name'])
        agent.setup(config_agent)
        metric = agent.compatibility_metric

        self.assertEqual(metric.__class__, ContextCompatibilityMetric)

        context = CSVContext()
        config['location']['path'] = self.temp_dir_path
        context.setup(config)

        # The confusingness of the naming is noted. context_for_user? Anything but this.
        context_entry = context.get_context('user2')

        self.assertAlmostEqual(context_entry['agent2'], 0.75, 3)


if __name__ == '__main__':
    unittest.main()

        