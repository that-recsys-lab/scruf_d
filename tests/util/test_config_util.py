import unittest
import toml
from scruf.util.config_util import is_valid_keys, get_value_from_keys, check_key_lists

SAMPLE_TOML = '''
# Test TOML

[a]
foo="bar"

[b]
bar="foo"

[c]

[c.1]
value=1

[c.2]
value=2

[c.3]
value=4

[d]
name="test"

[e]
list=[1,2,3]

'''

class ConfigUtilTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config = toml.loads(SAMPLE_TOML)

    def test_valid_paths(self):
        self.assertTrue(is_valid_keys(self.config, ['c', '3', 'value']))
        self.assertFalse(is_valid_keys(self.config, ['d', 'fake']))

    def test_get_value(self):
        self.assertEqual(get_value_from_keys(self.config, ['c', '3', 'value']), 4)
        self.assertEqual(get_value_from_keys(self.config, ['b', 'bar']), 'foo')
        self.assertEqual(get_value_from_keys(self.config, ['e', 'list']), [1, 2, 3])

    def test_check_paths(self):
        path_specs = [['c', '3', 'value'],
                     ['c', '1', 'value'],
                     ['b', 'bar']]

        self.assertTrue(check_key_lists(self.config, path_specs))
        path_specs.append(['e', 'lalalala'])
        self.assertFalse(check_key_lists(self.config, path_specs))


if __name__ == '__main__':
    unittest.main()
