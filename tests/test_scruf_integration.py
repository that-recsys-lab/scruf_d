import unittest
import tempfile
import pathlib
import toml
from scruf import Scruf
import json
from icecream import ic

# What to test:
# Configuration sets up a simple set of mechanisms
# We can run dummy data through it.
# Output is correct.
# History is saved and is correct.

TEST_CONFIG = '''# Sample configuration file for SCRUF-D
# For format reference only -- may not actually work in any given SCRUF-D version / data set

[location]
path = "."
overwrite = "true"

[data]
rec_filename = "recommendations.csv"
feature_filename = "item_features.csv"

[output]
filename = "history_file.json"

[parameters]
list_size = 2
iterations = -1 # -1 means run through all the users
initialize = "skip"
history_window_size = 50

[context]
context_class = "csv_context"

[context.properties]
compatibility_file = "compat_data.csv"

[feature]

[feature.f1]
name = "Feature 1"
protected_feature = "feature1"
protected_values = ["a", "b"]

[feature.f2]
name = "Feature 2"
protected_feature = "feature2"
protected_values = 1

[agent]

[agent.f1]
name = "Feature 1 Agent"
metric_class = "proportional_item"
compatibility_class = "context_compatibility"
choice_scorer_class = "zero_scorer"

[agent.f1.metric]
feature = "Feature 1"
proportion = 0.75

[agent.f2]
name = "Feature 2 Agent"
metric_class = "proportional_item"
compatibility_class = "context_compatibility"
choice_scorer_class = "zero_scorer"

[agent.f2.metric]
feature = "Feature 2"
proportion = 0.5

[allocation]
allocation_class = "most_compatible"

[choice]
choice_class = "null_choice"
'''

TEST_FEATURE_DATA = '''item1, feature1, a
item1, feature2, 1
item2, feature1, d
item3, feature1, a
item3, feature2, 1
item4, feature1, c
item4, feature2, 1
item5, feature1, d
item6, feature1, e
item6, feature2, 1
'''

TEST_CONTEXT_DATA = '''user1,Feature 1 Agent,0.0
user1,Feature 2 Agent,0.0
user2,Feature 1 Agent,1.0
user2,Feature 2 Agent,0.0
user3,Feature 1 Agent,0.5
user3,Feature 2 Agent,0.5
user4,Feature 1 Agent,1.0
user4,Feature 2 Agent,0.0
user5,Feature 1 Agent,0.0
user5,Feature 2 Agent,1.0
user6,Feature 1 Agent,0.5
user6,Feature 2 Agent,0.5
user7,Feature 1 Agent,0.25
user7,Feature 2 Agent,0.10
user8,Feature 1 Agent,0.75
user8,Feature 2 Agent,0.95
'''

TEST_FEATURE_FILE = 'item_features.csv'
TEST_HISTORY_FILE = 'history_file.json'
TEST_CONTEXT_FILE = 'compat_data.csv'

TEST_RECOMMENDATIONS = '''user1, item1, 5.0
user1, item2, 4.0
user1, item3, 3.0
user1, item4, 2.0
user2, item3, 4.9
user2, item4, 3.9
user2, item5, 2.9
user2, item6, 1.9
user3, item1, 4.8
user3, item2, 3.8
user3, item3, 2.8
user3, item4, 1.8
user4, item3, 4.7
user4, item4, 3.7
user4, item5, 2.7
user4, item6, 1.7
user5, item2, 4.6
user5, item4, 3.6
user5, item6, 2.6
user5, item1, 1.6
user6, item1, 4.5
user6, item3, 3.5
user6, item5, 2.5
user6, item2, 1.5
user7, item6, 4.4
user7, item5, 3.4
user7, item4, 2.4
user7, item3, 1.4
user8, item4, 4.3
user8, item3, 3.3
user8, item2, 2.3
user8, item1, 1.3
'''

TEST_RECOMMENDATION_FILE = 'recommendations.csv'

class ScrufIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)
        with open(self.temp_dir_path / TEST_FEATURE_FILE, 'w') as feature_file:
            feature_file.write(TEST_FEATURE_DATA)

        with open(self.temp_dir_path / TEST_RECOMMENDATION_FILE, 'w') as feature_file:
            feature_file.write(TEST_RECOMMENDATIONS)

        with open(self.temp_dir_path / TEST_CONTEXT_FILE, 'w') as feature_file:
            feature_file.write(TEST_CONTEXT_DATA)

        self.config = toml.loads(TEST_CONFIG)

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.temp_dir.cleanup()

    # After
    def test_configure(self):
        self.config['location']['path'] = self.temp_dir_path
        scruf = Scruf(self.config)
        self.assertIsNotNone(scruf.state)
        self.assertEqual(2, scruf.state.output_list_size)

    def test_setup(self):
        self.config['location']['path'] = self.temp_dir_path
        scruf = Scruf(self.config)
        scruf.setup_experiment()

        agent_names = scruf.state.agents.agent_names()
        self.assertListEqual(['Feature 1 Agent', 'Feature 2 Agent'], agent_names)
        self.assertEqual(None, scruf.state.user_data.current_user_index)

    def test_run_one(self):
        self.config['location']['path'] = self.temp_dir_path
        scruf = Scruf(self.config)
        scruf.setup_experiment()
        scruf.run_loop(iterations=1)
        scruf.cleanup_experiment()

        self.assertEqual(0, scruf.state.user_data.current_user_index)

        with open(self.temp_dir_path / TEST_HISTORY_FILE, 'r') as history_file:
            line = history_file.readline()

        history = json.loads(line)
        ic(history)

        # It should have processed user 1
        self.assertEqual(0, history['time'])
        self.assertEqual('user1', history['user'])
        self.assertIsInstance(history['allocation'], dict)
        alloc = history['allocation']
        # should be all zeros
        self.assertTrue(all([score == 0.0 for score in alloc['output'].values()]))
        choice = history['choice']
        choice_output = choice['output']['results']
        self.assertEqual(len(choice_output), 2)
        self.assertTrue(choice_output[0]['item'], 'item1')
        self.assertTrue(choice_output[1]['item'], 'item2')

    # Need to get proportional fairness working to test this.
    def test_run_two(self):
        self.config['location']['path'] = self.temp_dir_path
        scruf = Scruf(self.config)
        scruf.setup_experiment()
        scruf.run_loop(iterations=2)
        scruf.cleanup_experiment()

        self.assertEqual(1, scruf.state.user_data.current_user_index)

        with open(self.temp_dir_path / TEST_HISTORY_FILE, 'r') as history_file:
            line1 = history_file.readline()
            line2 = history_file.readline()

        history = json.loads(line2)
        ic(history)

        # It should have processed user 2
        self.assertEqual(1, history['time'])
        self.assertEqual('user2', history['user'])
        self.assertIsInstance(history['allocation'], dict)
        alloc = history['allocation']
        fairness = alloc['fairness scores']
        output = alloc['output']

if __name__ == '__main__':
    unittest.main()
