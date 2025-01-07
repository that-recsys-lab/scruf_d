import unittest
import tempfile
import pathlib
import toml
import random
from icecream import ic
from scruf.agent import BinaryPreferenceFunction, PerturbedBinaryPreferenceFunction, CascadePreferenceFunction, IndividualPreferenceFunction
from scruf.util import ResultList
from scruf.data import ItemFeatureData
import scruf
from scruf.history import ResultsHistory, ScrufHistory

TEST_FEATURE_DATA = '''
i1, feature1, a
i1, feature2, 1.5
i1, feature3, 1
i2, feature1, b
i2, feature2, 3.5
i2, feature3, 1
i3, feature1, a
i3, feature2, -1.2
i4, feature1, b
i4, feature2, 1
i5, feature1, a
i5, feature2, 2
'''

TEST_FEATURE_FILE = "test-features.csv"

TEST_FEATURE_CONFIG = f'''
[location]
path = "."

[data]
feature_filename = "test-features.csv"

[feature]

[feature.feature1]
name = "Protected values"
protected_feature = "feature1"
protected_values = ["a", "c"]

[feature.feature3]
name = "Protected binary"
protected_feature = "feature3"
protected_values = 1
'''

TEST_PROPERTIES = {
    "feature": "Protected values",
    "delta": 0.5
}
TEST_PROPERTIES2 = {
    "delta": 0.5
}

RESULT_TRIPLES1 = [('u1', 'i1', '3.5'),
                  ('u1', 'i2', '2.5'), # unprotected
                  ('u1', 'i3', '1.5'),
                  ]

RESULT_TRIPLES2 = [('u2', 'i4', '3.5'),
                  ('u2', 'i2', '2.5'),
                  ('u2', 'i1', '2.5')]

RESULT_TRIPLES3 = [('u3', 'i3', '1.5'),
                  ('u3', 'i1', '3.5'),
                  ('u3', 'i4', '3.5')]

RESULT_TRIPLES4 = [('u4', 'i3', '1.5'),
                   ('u4', 'i1', '3.5'),
                   ('u4', 'i5', '3.5')]



class PreferenceFunctionTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)
        with open(self.temp_dir_path / TEST_FEATURE_FILE, 'w') as feature_file:
            feature_file.write(TEST_FEATURE_DATA)

        self.config = toml.loads(TEST_FEATURE_CONFIG)

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.temp_dir.cleanup()

    def test_binary_preference(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.item_features = if_data

        bpf = BinaryPreferenceFunction()
        bpf.setup(TEST_PROPERTIES)
        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)

        rl_output = bpf.compute_preferences(rl1)
        entries = rl_output.get_results()

        self.assertAlmostEqual(0.5, entries[0].score)  # add assertion here
        self.assertAlmostEqual(0.0, entries[2].score)

    def test_perturbed_binary(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.item_features = if_data
        scruf.Scruf.state.rand = random.Random(230629)

        ppf = PerturbedBinaryPreferenceFunction()
        ppf.setup(TEST_PROPERTIES)
        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)

        rl_output = ppf.compute_preferences(rl1)
        entries = rl_output.get_results()
        top_entry = entries[0]
        self.assertEqual('i3', top_entry.item)
        self.assertAlmostEqual(0.533, top_entry.score, delta=0.001)

        last_entry = entries[2]
        self.assertEqual('i2', last_entry.item)
        self.assertAlmostEqual(-0.018, last_entry.score, delta=0.001)

    def test_cascade_preference(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.item_features = if_data
        scruf.Scruf.state.rand = random.Random(230629)

        ppf = CascadePreferenceFunction()
        ppf.setup(TEST_PROPERTIES)
        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES1)

        rl_output = ppf.compute_preferences(rl1)
        entries = rl_output.get_results()

        top_entry = entries[0]
        self.assertEqual('i1', top_entry.item)
        self.assertAlmostEqual(0.75, top_entry.score, delta=0.001)

        last_entry = entries[2]
        self.assertEqual('i2', last_entry.item)
        self.assertAlmostEqual(0.125, last_entry.score, delta=0.001)

    def test_individual_preference(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.item_features = if_data
        scruf.Scruf.state.rand = random.Random(230629)

        ppf = IndividualPreferenceFunction()
        ppf.setup(TEST_PROPERTIES2)
        rl1 = ResultList()
        rl1.setup(RESULT_TRIPLES4)

        self.rlist1 = ResultList()
        self.rlist2 = ResultList()
        self.rlist3 = ResultList()
        self.rlist4 = ResultList()

        self.rlist1.setup(RESULT_TRIPLES1)
        self.rlist2.setup(RESULT_TRIPLES2)
        self.rlist3.setup(RESULT_TRIPLES3)
        self.rlist4.setup(RESULT_TRIPLES4)

        rhist = ResultsHistory(5)
        rhist.add_items([self.rlist1, self.rlist2, self.rlist3, self.rlist4])
        hist = ScrufHistory()
        hist.choice_output_history = rhist

        rl_output = ppf.compute_preferences(hist, rl1)
        entries = rl_output.get_results()

        top_entry = entries[0]
        self.assertEqual('i5', top_entry.item)
        self.assertAlmostEqual(0.5, top_entry.score, delta=0.001)

        last_entry = entries[2]
        self.assertEqual('i1', last_entry.item)
        self.assertAlmostEqual(0.0, last_entry.score, delta=0.001)


if __name__ == '__main__':
    unittest.main()
