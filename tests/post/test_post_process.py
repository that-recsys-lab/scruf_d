import unittest
import toml
from pathlib import Path
import scruf

from scruf.post import PostProcessorFactory, NullPostProcessor, DefaultPostProcessor

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
'''

SAMPLE_PROPERTIES3 = '''
[post]
postprocess_class = "ndcg"

[post.properties]
filename="test-output.csv"
threshold="none"
binary="false"
'''


class PostProcessorTestCase(unittest.TestCase):
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

        post.history = post.read_history(Path('../../jupyter/sample_output.json'))
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

        post.history = post.read_history(Path('../../jupyter/sample_output.json'))
        post.history_to_dataframe()
        post.compute_ndcg_column()

        ndcg_col = post.dataframe[('nDCG', 'All')]

        ic(ndcg_col)

        self.assertEqual(1.0, ndcg_col[0])


if __name__ == '__main__':
    unittest.main()
