import unittest
import toml

from scruf.data import ContextFactory, NullContext

SAMPLE_PROPERTIES = '''
[context]
context_class = "null_context"
'''


class ContextClassTestCase(unittest.TestCase):
    def test_context_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        ctx_name = config['context']['context_class']
        choice = ContextFactory.create_context_class(ctx_name)

        self.assertEqual(choice.__class__, NullContext)


if __name__ == '__main__':
    unittest.main()
