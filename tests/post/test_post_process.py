import unittest
import toml
from pathlib import Path
import scruf

from scruf.post import PostProcessorFactory, NullPostProcessor, DefaultPostProcessor
from scruf.data import ItemFeatureData

from icecream import ic

SAMPLE_PROPERTIES = '''
[post]
postprocess_class = "null"
'''

SAMPLE_PROPERTIES2 = '''
[post]
postprocess_class = "default"

[post.properties]
filename="test-output.csv"
summary_filename="test-summary.csv"
'''

SAMPLE_PROPERTIES3 = '''
[post]
postprocess_class = "ndcg"

[post.properties]
filename="test-output.csv"
summary_filename="test-summary.csv"
threshold="none"
binary="false"
'''

SAMPLE_PROPERTIES4 = '''
[data]
feature_filename = "items.csv"

[feature]

[feature.one]
name = "1"
protected_feature = "1"
protected_values = [1]

[feature.two]
name = "2"
protected_feature = "2"
protected_values = [1]

[agent]

[agent.country]
name = "country"
metric_class = "proportional_item"
compatibility_class = "context_compatibility"
preference_function_class = "binary_preference"

[agent.country.metric]
feature = "2"
proportion = 0.2

[agent.country.preference]
delta = 0.3
feature = "COUNTRY_low_pfr"

[post]
postprocess_class = "exposure"

[post.properties]
filename="test-output.csv"
summary_filename="test-summary.csv"
threshold="none"
binary="false"
'''


class PostProcessorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.module_path = module_path = Path(scruf.__file__).parent
        self.history_path = module_path / Path('../jupyter/sample_output.json')
        self.feature_path = module_path / Path('../jupyter/items.csv')

    def test_post_process_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['post']['postprocess_class']
        post = PostProcessorFactory.create_post_processor(alg_name)

        self.assertEqual(post.__class__, NullPostProcessor)

        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['post']['postprocess_class']
        post = PostProcessorFactory.create_post_processor(alg_name)
        post.setup(config['post']['properties'])

        self.assertEqual(post.__class__, DefaultPostProcessor)
        self.assertEqual("test-output.csv", post.get_property('filename'))

    def test_create_dataframe(self):
        config = toml.loads(SAMPLE_PROPERTIES2)
        alg_name = config['post']['postprocess_class']
        post = PostProcessorFactory.create_post_processor(alg_name)
        post.setup(config['post']['properties'])

        post.history = post.read_history(self.history_path)
        post.history_to_dataframe()
        df = post.dataframe

        self.assertEqual(200, df.shape[0])
        self.assertEqual(9, df.shape[1])

        self.assertEqual(0.0, df.loc[0, ('Allocation', '1')])

    def test_ndcg(self):
        fake_state = scruf.Scruf.ScrufState(None)
        fake_state.output_list_size = 10
        scruf.Scruf.state = fake_state

        config = toml.loads(SAMPLE_PROPERTIES3)
        alg_name = config['post']['postprocess_class']
        post = PostProcessorFactory.create_post_processor(alg_name)
        post.setup(config['post']['properties'])

        post.history = post.read_history(self.history_path)
        post.history_to_dataframe()
        post.compute_ndcg_column()

        ndcg_col = post.dataframe[('nDCG', 'All')]

        self.assertEqual(1.0, ndcg_col[0])

    def test_exposure(self):
        config = toml.loads(SAMPLE_PROPERTIES4)

        fake_state = scruf.Scruf.ScrufState(None)
        fake_state.output_list_size = 10
        scruf.Scruf.state = fake_state
        scruf.Scruf.state.agents = []
        scruf.Scruf.state.config = config

        # Manual setup of the feature data
        ifd = ItemFeatureData()
        ifd.feature_file = self.feature_path
        ifd.load_item_features()
        ifd.known_features = {}
        ifd.setup_features(config['feature'])
        ifd.setup_indices()
        scruf.Scruf.state.item_features = ifd

        alg_name = config['post']['postprocess_class']
        post = PostProcessorFactory.create_post_processor(alg_name)
        post.setup(config['post']['properties'])

        post.history = post.read_history(self.history_path)
        post.history_to_dataframe()
        post.compute_ndcg_column()
        post.compute_fairness_columns(post.history)

        fairness_col = post.dataframe[('Fairness Metric', '2')]

        self.assertAlmostEqual(0.1, fairness_col[0], places=3)


if __name__ == '__main__':
    unittest.main()
