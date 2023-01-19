import unittest

from scruf.agent import AlwaysOneCompatibilityMetric, AlwaysZeroCompatibilityMetric, CompatibilityMetricFactory
from scruf.util import PropertyMismatchError, UnregisteredCompatibilityMetricError, \
    InvalidCompatibilityMetricError

COMPATIBILITY_PROPERTIES_EXTRA = \
{
    'extra_prop': 42
}

# Note: we are not testing the setting of properties because we don't have any metrics with properties defined yet.
class CompatibilityMetricTestCase(unittest.TestCase):
    def test_metric_creation(self):
        metric = AlwaysOneCompatibilityMetric()
        metric.setup(dict())
        self.assertEqual(len(metric.get_property_names()), 0)

        self.assertEqual(metric.compute_compatibility(None), 1.0)

    def test_metric_property_mismatch(self):
        metric = AlwaysZeroCompatibilityMetric()

        with self.assertRaises(PropertyMismatchError):
            metric.setup(COMPATIBILITY_PROPERTIES_EXTRA)

    def test_compatibility_metric_factory(self):
        metric = CompatibilityMetricFactory.create_compatibility_metric('always_one')
        self.assertEqual(metric.__class__, AlwaysOneCompatibilityMetric)

        with self.assertRaises(UnregisteredCompatibilityMetricError):
            metric = CompatibilityMetricFactory.create_compatibility_metric('foo')

        with self.assertRaises(InvalidCompatibilityMetricError):
            CompatibilityMetricFactory.register_compatibility_metric('wrong', PropertyMismatchError)

if __name__ == '__main__':
    unittest.main()
