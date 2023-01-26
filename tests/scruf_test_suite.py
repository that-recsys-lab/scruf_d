import unittest

from agent.test_fairness_agents import AgentTestCase
from agent.test_fairness_metric import FairnessMetricTestCase
from agent.test_compatibility_metric import CompatibilityMetricTestCase
from allocation.test_allocation_mechanism import AllocationMechanismTestCase
from choice.test_choice_mechanism import ChoiceMechanismTestCase
from data.test_item_feature import ItemFeatureTestCase
from history.test_results_history import TestResultsHistory
from history.test_scruf_history import ScrufHistoryTestCase
from util.test_hcollection import TestHistoryCollection
from util.test_result_list import ResultListTestCase
from util.test_config_util import ConfigUtilTestCase


def suite():
    suite = unittest.TestSuite()
    agent_tests = unittest.defaultTestLoader.loadTestsFromTestCase(AgentTestCase)
    suite.addTest(agent_tests)
    metric_tests = unittest.defaultTestLoader.loadTestsFromTestCase(FairnessMetricTestCase)
    suite.addTest(metric_tests)
    compat_test = unittest.defaultTestLoader.loadTestsFromTestCase(CompatibilityMetricTestCase)
    suite.addTest(compat_test)
    alloc_test = unittest.defaultTestLoader.loadTestsFromTestCase(AllocationMechanismTestCase)
    suite.addTest(alloc_test)
    choice_test = unittest.defaultTestLoader.loadTestsFromTestCase(ChoiceMechanismTestCase)
    suite.addTest(choice_test)
    if_test = unittest.defaultTestLoader.loadTestsFromTestCase(ItemFeatureTestCase)
    suite.addTest(if_test)
    rhist_tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestResultsHistory)
    suite.addTest(rhist_tests)
    shist_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ScrufHistoryTestCase)
    suite.addTest(shist_tests)
    hcoll_tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestHistoryCollection)
    suite.addTest(hcoll_tests)
    rlist_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ResultListTestCase)
    suite.addTest(rlist_tests)
    conf_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ConfigUtilTestCase)
    suite.addTest(conf_tests)

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

