import unittest

import scruf, pathlib, tempfile, toml

from scruf.agent import ItemFeatureFairnessMetric, FairnessMetricFactory, ProportionalItemFM, \
    MeanReciprocalRankFM, DisparateExposureFM
from scruf.util import PropertyMismatchError, UnregisteredFairnessMetricError, InvalidFairnessMetricError, \
    ResultList
from scruf.history import ResultsHistory, ScrufHistory
from scruf.data import ItemFeatureData

from numpy import log2, mean

ITEM_FEATURE_PROPERTIES = \
{
    'feature': 'f1',
    'proportion': 0.75
}

ITEM_FEATURE_PROPERTIES_MISSING = \
{
}

ITEM_FEATURE_PROPERTIES_EXTRA = \
{
    'feature': 'test_feature',
    'proportion': 0.5,
    'extra_prop': 42
}

ITEM_FEATURE_PROPERTIES2 = \
{
    'feature': 'f1',
    'target': 0.75
}

ITEM_FEATURE_PROPERTIES3 = \
{
    'feature': 'f1',
    'target': 0.75,
    'n_protected': 0.6
}

# 3 protected
RESULT_TRIPLES_1 = [('u1', 'i1', '3.5'),
                  ('u1', 'i2', '3.0'),
                  ('u1', 'i3', '2.5'),
                  ('u1', 'i4', '4.0'),
                  ('u1', 'i5', '5.0'),
                  ]

# 3 protected
RESULT_TRIPLES_2 = [('u2', 'i11', '2.0'),
                  ('u2', 'i12', '3.0'),
                  ('u2', 'i3', '1.5'),
                  ('u2', 'i14', '4.0'),
                  ('u2', 'i5', '1.0'),
                  ]

# 3 protectec
RESULT_TRIPLES_3 = [('u3', 'i21', '3.5'),
                  ('u3', 'i12', '3.0'),
                  ('u3', 'i3', '2.5'),
                  ('u3', 'i24', '4.0'),
                  ('u3', 'i25', '0.5'),
                  ]

TEST_FEATURE_CONFIG = f'''
[location]
path = "."

[data]
feature_filename = "test-features.csv"

[feature]

[feature.feature1]
name = "f1"
protected_feature = "f1"
protected_values = 1
'''

# odd items have the feature
SAMPLE_FEATURES = '''
i1,f1,1
i2,f1,0
i3,f1,1
i4,f1,0
i5,f1,1
i11,f1,1
i12,f1,0
i21,f1,1
i24,f1,0
i25,f1,1
'''

TEST_FEATURE_FILE = "test-features.csv"

class FairnessMetricTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Get the path to the temporary directory
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)
        with open(self.temp_dir_path / TEST_FEATURE_FILE, 'w') as feature_file:
            feature_file.write(SAMPLE_FEATURES)

        self.config = toml.loads(TEST_FEATURE_CONFIG)

    def tearDown(self):
        # Delete the temporary directory and all its contents
        self.temp_dir.cleanup()

    def test_metric_creation(self):
        metric = ProportionalItemFM()
        metric.setup(ITEM_FEATURE_PROPERTIES)
        self.assertEqual(set(metric.get_property_names()),
                          {'feature', 'proportion'})

        props = metric.get_properties()
        self.assertEqual(props['feature'], ITEM_FEATURE_PROPERTIES['feature'])
        #self.assertEquals(props['protected_values'], ITEM_FEATURE_PROPERTIES['protected_values'])

    def test_metric_property_mismatch(self):
        metric = ProportionalItemFM()

        with self.assertRaises(PropertyMismatchError):
            metric.setup(ITEM_FEATURE_PROPERTIES_MISSING)

        with self.assertRaises(PropertyMismatchError):
            metric.setup(ITEM_FEATURE_PROPERTIES_EXTRA)

    def test_fairness_metric_factory(self):
        metric = FairnessMetricFactory.create_fairness_metric('proportional_item')
        self.assertEqual(metric.__class__, ProportionalItemFM)

        with self.assertRaises(UnregisteredFairnessMetricError):
            metric = FairnessMetricFactory.create_fairness_metric('foo')

        with self.assertRaises(InvalidFairnessMetricError):
            FairnessMetricFactory.register_fairness_metric('wrong', PropertyMismatchError)

    def test_proportional_item_fm(self):
        metric = ProportionalItemFM()
        metric.setup(ITEM_FEATURE_PROPERTIES)

        self.rlist1 = ResultList()
        self.rlist2 = ResultList()
        self.rlist3 = ResultList()

        self.rlist1.setup(RESULT_TRIPLES_1)
        self.rlist2.setup(RESULT_TRIPLES_2)
        self.rlist3.setup(RESULT_TRIPLES_3)

        rhist = ResultsHistory(5)
        rhist.add_items([self.rlist3, self.rlist2, self.rlist1, self.rlist3, self.rlist2])
        hist = ScrufHistory()
        hist.choice_output_history = rhist

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)
        scruf.Scruf.state.item_features = if_data

        fairness = metric.compute_fairness(hist)

        # (items with feature / total items) / target proportion
        correct_score = (15.0 / 25.0) / 0.75

        self.assertAlmostEqual(correct_score, fairness, 4)

    def test_mrr_fm(self):
        metric = MeanReciprocalRankFM()
        metric.setup(ITEM_FEATURE_PROPERTIES2)

        self.rlist1 = ResultList()
        self.rlist2 = ResultList()
        self.rlist3 = ResultList()

        self.rlist1.setup(RESULT_TRIPLES_1)
        self.rlist2.setup(RESULT_TRIPLES_2)
        self.rlist3.setup(RESULT_TRIPLES_3)

        rhist = ResultsHistory(5)
        rhist.add_items([self.rlist3, self.rlist2, self.rlist1, self.rlist3, self.rlist2])
        hist = ScrufHistory()
        hist.choice_output_history = rhist

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)
        scruf.Scruf.state.item_features = if_data

        fairness = metric.compute_fairness(hist)

        # l3, l2, l1, l3, l2
        # l3 has RR of 1/2, l2 = 1/3, l1 = 1/1
        correct_score = ((1/2 + 1/3 + 1 + 1/2 + 1/3) / 5) / 0.75

        self.assertAlmostEqual(correct_score, fairness, 4)

    def test_disparate_exposure_fm(self):
        metric = DisparateExposureFM()
        metric.setup(ITEM_FEATURE_PROPERTIES3)

        self.rlist1 = ResultList()
        self.rlist2 = ResultList()
        self.rlist3 = ResultList()

        self.rlist1.setup(RESULT_TRIPLES_1)
        self.rlist2.setup(RESULT_TRIPLES_2)
        self.rlist3.setup(RESULT_TRIPLES_3)

        rhist = ResultsHistory(5)
        rhist.add_items([self.rlist3, self.rlist2, self.rlist1, self.rlist3, self.rlist2])
        hist = ScrufHistory()
        hist.choice_output_history = rhist

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        if_data = ItemFeatureData()
        self.config['location']['path'] = self.temp_dir_path
        if_data.setup(self.config)
        scruf.Scruf.state.item_features = if_data

        fairness = metric.compute_fairness(hist)

        # l3, l2, l1, l3, l2
        # ranks in l3 are 2, 4, 5
        # ranks in l2 are 3, 4, 5
        # ranks in l1 are 1, 3, 5,
        prot_ranks = [2, 4, 5, 3, 4, 5, 1, 3, 5, 2, 4, 5, 3, 4, 5]
        unprot_ranks = [1, 3, 1, 2, 2, 4, 1, 3, 1, 2]
        prot_rr_values = [1/log2(rank + 1) for rank in prot_ranks]
        unprot_rr_values = [1/log2(rank + 1) for rank in unprot_ranks]
        utility_prot = sum(prot_rr_values)
        utility_unprot = sum(unprot_rr_values)
        utility_ratio = (utility_prot / 0.6) / (utility_unprot / 0.4)
        correct_score = utility_ratio / 0.75

        self.assertAlmostEqual(correct_score, fairness, 4)

if __name__ == '__main__':
    unittest.main()
