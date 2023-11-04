import unittest

from scruf.agent import ItemFeatureFairnessMetric, FairnessMetricFactory, ProportionalItemFM
from scruf.util import PropertyMismatchError, UnregisteredFairnessMetricError, InvalidFairnessMetricError

ITEM_FEATURE_PROPERTIES = \
{
    'feature': 'test_feature',
    'proportion': 0.5
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

class FairnessMetricTestCase(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
