import unittest

from scruf.agent import ItemFeatureFairnessMetric, FairnessMetricFactory, ProportionalItemFM
from scruf.util import PropertyMismatchError, UnregisteredFairnessMetricError, InvalidFairnessMetricError

ITEM_FEATURE_PROPERTIES = \
{
    'protected_feature': 'test_feature',
    'protected_values': ['f1', 'f2', 'f3']
}

ITEM_FEATURE_PROPERTIES_MISSING = \
{
    'protected_feature': 'test_feature'
}

ITEM_FEATURE_PROPERTIES_EXTRA = \
{
    'protected_feature': 'test_feature',
    'protected_values': ['f1', 'f2', 'f3'],
    'extra_prop': 42
}

class FairnessMetricTestCase(unittest.TestCase):
    def test_metric_creation(self):
        metric = ItemFeatureFairnessMetric()
        metric.setup(ITEM_FEATURE_PROPERTIES)
        self.assertEquals(set(metric.get_property_names()),
                          {'protected_feature', 'protected_values'})

        props = metric.get_properties()
        self.assertEquals(props['protected_feature'], ITEM_FEATURE_PROPERTIES['protected_feature'])
        self.assertEquals(props['protected_values'], ITEM_FEATURE_PROPERTIES['protected_values'])

    def test_metric_property_mismatch(self):
        metric = ItemFeatureFairnessMetric()

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

if __name__ == '__main__':
    unittest.main()
