import unittest
import tempfile
import toml
from scruf.history import ScrufHistory


def make_config(path):
    TEST_CONFIG = f'''
[location]
path = "{path}"
overwrite = "true"

[data]
rec_filename = "data/recommendations.txt"
feature_filename = "data/item_features.txt"

[output]
filename = "history_file.json"

[parameters]
list_size = 10
iterations = -1 # -1 means run through all the users
initialize = "skip"
history_window_size = 50

[agent]

[agent.country]
name = "Country"
metric_class = "proportional_fair"
compatibility = "entropy"

[agent.country.metric]
protected_feature = "country"
protected_values = ["ug", "th", "ke", "ha"]

[agent.sector]
name = "Sector"
metric_class = "list_exposure"
compatibility = "entropy"

[agent.sector.metric]
protected_feature = "sector"
protected_values = [7, 18, 35]

[agent.loan_size]
name = "Loan Size"
metric_class = "list_exposure"
compatibility = "risk_aversion"

[agent.loan_size.metric]
protected_feature = "bucket5"
protected_values = [1]

[allocation]
algorithm = "lottery_single"
history_length = 10

[choice]
algorithm = "fixed_utility"
delta = 0.5
alpha = 0.2
'''
    return TEST_CONFIG


class ScrufHistoryTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = self.temp_dir.name
        config_text = make_config(self.temp_dir_path)
        self.config = toml.loads(config_text)

    def test_create_history(self):
        self.history = ScrufHistory()
        self.history.setup(self.config)
        self.assertIsNotNone(self.history.allocation_history)
        self.assertEqual(self.history.allocation_history.window_size, 50)
        self.assertIsNotNone(self.history.choice_history)
        self.assertIsNotNone(self.history.fairness_history)
        self.assertIsNotNone(self.history.recommendation_input_history)
        self.assertIsNotNone(self.history.recommendation_output_history)

        self.assertFalse(self.history._history_file.closed)

    # TODO: Should test for the updating of the file

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.history.cleanup()
        self.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
