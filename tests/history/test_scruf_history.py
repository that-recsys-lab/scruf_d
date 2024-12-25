import unittest
import tempfile
import toml
from scruf.history import ScrufHistory
import scruf
from scruf.data import BulkLoadedUserData
from scruf.util import Ballot, BallotCollection, ResultEntry, ResultList
from icecream import ic
from pathlib import Path
from pyarrow import csv

'''
fair_output = [
    current_time,
    current_user,
    "agent",
    agent,
    alloc["fairness scores"][agent],
    "NaN",
    "fairness",
]
'''

USER_DATA = '''158052,910,4
158052,3052,4
158052,1269,0.5
158052,913,4.5
158052,1663,4
260447,380,3
260447,296,5
260447,588,5
260447,36,4
260447,165,5
260447,344,2
260447,150,5
260447,153,3
260447,737,2
260447,527,5
260447,592,3
'''

USER_FILE_NAME = 'test_user.csv'

def make_config(path):
    TEST_CONFIG = f'''
[location]
path = "{path}"
overwrite = "true"

[data]
rec_filename = "test_user.csv"
feature_filename = "data/item_features.txt"

[output]
filename = "history_file.csv"

[parameters]
list_size = 3
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
        self.temp_dir_path = Path(self.temp_dir.name)
        config_text = make_config(self.temp_dir_path)
        with open(self.temp_dir_path / USER_FILE_NAME, 'w') as fl:
            fl.write(USER_DATA)
        self.config = toml.loads(config_text)



    def test_update_history(self):
        self.history = ScrufHistory()
        self.history.setup(self.config)
        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.user_data = BulkLoadedUserData()
        self.config['location']['path'] = self.temp_dir_path
        scruf.Scruf.state.user_data.setup(self.config)
        iter = scruf.Scruf.state.user_data.user_iterator()
        iter.__next__()

        self.history.allocation_history.add_item(
            {"fairness scores": {"agent1": 0.1, "agent2": 0.9},
             "compatibility scores": {"agent1": 0.2, "agent2": 0.3},
             "output": {"agent1": 1.0, "agent2": 0.0}})

        bc1 = BallotCollection()
        rec_prefs = ResultList()
        rec_prefs.add_result(158052, 910, 4)
        rec_prefs.add_result(158052, 3052, 3)

        b1 = Ballot('__rec', rec_prefs)
        bc1.set_from_ballot_list([b1])

        self.history.choice_input_history.add_item(bc1)

        bc2 = BallotCollection()
        rec_prefs = ResultList()
        rec_prefs.add_result(158052, 3052, 4)
        rec_prefs.add_result(158052, 910, 3)

        b2 = Ballot('results', rec_prefs)
        bc2.set_from_ballot_list([b2])

        self.history.choice_output_history.add_item(rec_prefs)

        self.history.write_current_state()

        self.history.cleanup(no_compress=True)

        # what are the arguments to read_csv to treat the first line as data?
        table = csv.read_csv(self.temp_dir_path / self.history.history_file_name,
                             csv.ReadOptions(column_names=['time', 'user', 'type', 'item',
                                                           'score', 'rank', 'var']))

        hist_dicts = table.to_pylist()

        self.assertEqual(hist_dicts[0]['user'], 158052)
        self.assertEqual(hist_dicts[0]['item'], ' agent1')

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.history.cleanup()
        self.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()



'''

        alloc = self.allocation_history.get_most_recent()
        choice_input = self.choice_input_history.get_most_recent()
        choice_output = self.choice_output_history.get_most_recent()
'''

'''
    def test_create_history(self):
        self.history = ScrufHistory()
        self.history.setup(self.config)
        self.assertIsNotNone(self.history.allocation_history)
        self.assertEqual(self.history.allocation_history.window_size, 50)
        self.assertIsNotNone(self.history.choice_output_history)
        self.assertIsNotNone(self.history.choice_input_history)

        self.assertFalse(self.history._history_file.closed)
'''
