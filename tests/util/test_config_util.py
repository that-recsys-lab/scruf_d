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

[f]
b1 = "True"
b2 = "true"
b4 = true
b5 = "False"
b6 = "false"
b8 = false

'''

class ConfigUtilTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config = toml.loads(SAMPLE_TOML)

    def test_valid_paths(self):
        self.assertTrue(is_valid_keys(['c', '3', 'value'], config=self.config))
        self.assertFalse(is_valid_keys(['d', 'fake'], self.config))

    def test_get_value(self):
        self.assertEqual(get_value_from_keys(['c', '3', 'value'], config=self.config), 4)
        self.assertEqual(get_value_from_keys(['b', 'bar'], config=self.config), 'foo')
        self.assertEqual(get_value_from_keys(['e', 'list'], config=self.config), [1, 2, 3])

    def test_check_paths(self):
        path_specs = [['c', '3', 'value'],
                     ['c', '1', 'value'],
                     ['b', 'bar']]

        self.assertTrue(check_key_lists(path_specs, config=self.config))
        path_specs.append(['e', 'lalalala'])
        self.assertFalse(check_key_lists(path_specs, config=self.config))

    def test_boolean(self):
        self.assertTrue(get_value_from_keys(['f', 'b1'], config=self.config))
        self.assertFalse(get_value_from_keys(['f', 'b5'], config=self.config))
        self.assertTrue(get_value_from_keys(['f', 'b2'], config=self.config))
        self.assertFalse(get_value_from_keys(['f', 'b6'], config=self.config))
        self.assertTrue(get_value_from_keys(['f', 'b4'], config=self.config))
        self.assertFalse(get_value_from_keys(['f', 'b8'], config=self.config))


if __name__ == '__main__':
    unittest.main()
