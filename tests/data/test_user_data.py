import unittest
import tempfile
import pathlib
import toml
from scruf.data import BulkLoadedUserData
from icecream import ic

TEST_USER_DATA = '''user1, item1, 4.0
user1, item2, 3.5
user1, item3, 1.0
user2, item3, 4.8
user2, item2, 4.0
user2, item1, 1.2
user3, item2, 3.3
user3, item1, 2.3
user3, item3, 1.0
'''

TEST_USER_FILE = "test-users.csv"

TEST_USER_CONFIG = f'''
[location]
path = "."

[data]
rec_filename = "test-users.csv"
'''

class ItemFeatureTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)
        with open(self.temp_dir_path / TEST_USER_FILE, 'w') as feature_file:
            feature_file.write(TEST_USER_DATA)

        self.config = toml.loads(TEST_USER_CONFIG)

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.temp_dir.cleanup()

    def test_load_users(self):
        user_data = BulkLoadedUserData()
        self.config['location']['path'] = self.temp_dir_path
        user_data.setup(self.config)
        self.assertEqual(user_data.current_user_index, None)
        self.assertEqual(user_data.arrival_sequence, ['user1', 'user2', 'user3'])
        user3_results = user_data.user_table['user3'].get_results()
        self.assertEqual(len(user3_results), 3)
        user3_second_entry = user3_results[1]
        self.assertEqual(user3_second_entry.user, 'user3')
        self.assertEqual(user3_second_entry.item, 'item1')
        self.assertEqual(user3_second_entry.score, 2.3)

    def test_iterate(self):
        user_data = BulkLoadedUserData()
        self.config['location']['path'] = self.temp_dir_path
        user_data.setup(self.config)
        self.assertEqual(user_data.arrival_sequence, ['user1', 'user2', 'user3'])
        iter = user_data.user_iterator()
        iter.__next__()
        res_list = iter.__next__()
        self.assertEqual(user_data.current_user_index, 1)
        current_results = res_list.get_results()
        current_first_entry = current_results[0]
        self.assertEqual(current_first_entry.user, 'user2')
        self.assertEqual(current_first_entry.item, 'item3')
        self.assertEqual(current_first_entry.score, 4.8)

        iter2 = user_data.user_iterator(iterations=1)
        for res_list in iter2:
            ic(res_list.get_results()[0])

        self.assertEqual(user_data.current_user_index, 0)

        iter3 = user_data.user_iterator(iterations=1, restart=False)
        for res_list in iter3:
            ic(res_list.get_results()[0])

        self.assertEqual(user_data.current_user_index, 1)

if __name__ == '__main__':
    unittest.main()
