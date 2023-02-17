import unittest
import toml
import tempfile
import pathlib

from scruf.data import ContextFactory, NullContext

SAMPLE_PROPERTIES = '''
[context]
context_class = "null_context"
'''

TEST_COMPATIBILITIES_FILE = 'compatibilities.csv'

SAMPLE_COMPATIBILITIES = '''
user1,agent1,1.0
user1,agent2,0.5
user1,agent3,0.0
user2,agent1,0.55
user2,agent2,0.75
user2,agent3,0.95
'''


class ContextClassTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)
        with open(self.temp_dir_path / TEST_COMPATIBILITIES_FILE, 'w') as feature_file:
            feature_file.write(SAMPLE_COMPATIBILITIES)

       # self.config = toml.loads(TEST_FEATURE_CONFIG)

    def test_context_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        ctx_name = config['context']['context_class']
        choice = ContextFactory.create_context_class(ctx_name)

        self.assertEqual(choice.__class__, NullContext)


if __name__ == '__main__':
    unittest.main()
