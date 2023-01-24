import unittest
import tempfile
import pathlib
import toml
from scruf.data import ItemFeatureData

TEST_FEATURE_DATA = '''
item1, feature1, a
item1, feature2, 1.5
item1, feature3, 1
item2, feature1, b
item2, feature2, 3.5
item2, feature3, 1
item3, feature1, a
item3, feature2, -1.2
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

class ItemFeatureTestCase(unittest.TestCase):
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

    def test_load_features(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)
        self.assertEqual(if_data.item_feature_index['item1']['feature1'], 'a')
        self.assertEqual(if_data.item_feature_index['item3']['feature2'], -1.2)

    def test_value_index(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)
        self.assertSetEqual(if_data.feature_value_index['feature1']['a'], {'item1','item3'})
        self.assertSetEqual(if_data.feature_value_index['feature1']['q'], set())

    def test_protected(self):
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)

        self.assertSetEqual(if_data.protected_item_index['Protected values'], {'item1','item3'})
        self.assertSetEqual(if_data.protected_item_index['Protected binary'], {'item1', 'item2'})


if __name__ == '__main__':
    unittest.main()
