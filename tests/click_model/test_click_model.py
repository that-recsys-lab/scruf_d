import unittest
import toml
from scruf.click_model import ClickModelFactory, NullClickModel, TopItemModel, UniformRandomModel
from scruf.util import ResultList
import scruf
import random
from icecream import ic

SAMPLE_PROPERTIES = '''
[click]
click_class = "null_click"
'''

SAMPLE_PROPERTIES1 = '''
[click]
click_class = "top_item_click"
'''

SAMPLE_PROPERTIES2 = '''
[click]
click_class = "uniform_random_click"

[click.properties]
reserve_probability=1.0
'''


class ClickModelTestCase(unittest.TestCase):
    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['click']['click_class']
        click_model = ClickModelFactory.create_click_model(alg_name)

        self.assertEqual(click_model.__class__, NullClickModel)

        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['click']['click_class']
        click_model = ClickModelFactory.create_click_model(alg_name)
        click_model.setup(config['click']['properties'])

        self.assertEqual(click_model.__class__, UniformRandomModel)
        self.assertAlmostEqual(click_model.get_property('reserve_probability'), 1.0)

    def test_null_click(self):
        scruf.Scruf(None)
        scruf.Scruf.state.rand = random.Random(420)
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['click']['click_class']
        click_model = ClickModelFactory.create_click_model(alg_name)

        result_triples = [('u1', 'i1', 1.0), ('u1', 'i2', 0.5), ('u1', 'i3', 0.2)]
        result = ResultList()
        result.setup(result_triples, presorted=True)
        output = click_model.generate_clicks(result)
        output_entries = output.get_results()

        self.assertEqual(3, len(output_entries))
        self.assertEqual('i1', output_entries[0].item)
        self.assertEqual('i3', output_entries[2].item)

    def test_uniform_reserve(self):
        scruf.Scruf(None)
        scruf.Scruf.state.rand = random.Random(420)
        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['click']['click_class']
        click_model = ClickModelFactory.create_click_model(alg_name)
        click_model.setup(config['click']['properties'])

        result_triples = [('u1', 'i1', 1.0), ('u1', 'i2', 0.5), ('u1', 'i3', 0.2)]
        result = ResultList()
        result.setup(result_triples, presorted=True)
        output = click_model.generate_clicks(result)
        # ic(output)
        output_entries = output.get_results()

        self.assertEqual(0, len(output_entries))


if __name__ == '__main__':
    unittest.main()
