import unittest

from agent.test_fairness_agents import AgentTestCase
from agent.test_fairness_metric import FairnessMetricTestCase
from agent.test_compatibility_metric import CompatibilityMetricTestCase
from agent.test_context_compatibility import ContextCompatibilityTestCase
from agent.test_preference_function import PreferenceFunctionTestCase
from allocation.test_allocation_mechanism import AllocationMechanismTestCase
from choice.test_choice_mechanism import ChoiceMechanismTestCase
from choice.test_whalrus_wrapper import WhalrusWrapperTestCase
from choice.test_greedy_sublist import GreedySublistTestCase
from choice.test_fair_rerank import FARTestCase
from data.test_context_class import ContextClassTestCase
from data.test_item_feature import ItemFeatureTestCase
from data.test_user_data import UserDataTestCase
from history.test_results_history import TestResultsHistory
from history.test_scruf_history import ScrufHistoryTestCase
from util.test_hcollection import TestHistoryCollection
from util.test_result_list import ResultListTestCase
from util.test_config_util import ConfigUtilTestCase
from util.test_score_dict import ScoreDictTestCase
from util.test_ballot_collection import TestBallotCollection
from post.test_post_process import PostProcessorTestCase
from test_scruf_integration import ScrufIntegrationTestCase


def suite():
    suite = unittest.TestSuite()
    agent_tests = unittest.defaultTestLoader.loadTestsFromTestCase(AgentTestCase)
    suite.addTest(agent_tests)
    metric_tests = unittest.defaultTestLoader.loadTestsFromTestCase(FairnessMetricTestCase)
    suite.addTest(metric_tests)
    compat_test = unittest.defaultTestLoader.loadTestsFromTestCase(CompatibilityMetricTestCase)
    suite.addTest(compat_test)
    cx_compat_test = unittest.defaultTestLoader.loadTestsFromTestCase(ContextCompatibilityTestCase)
    suite.addTest(cx_compat_test)
    pref_test = unittest.defaultTestLoader.loadTestsFromTestCase(PreferenceFunctionTestCase)
    suite.addTest(pref_test)
    alloc_test = unittest.defaultTestLoader.loadTestsFromTestCase(AllocationMechanismTestCase)
    suite.addTest(alloc_test)
    choice_test = unittest.defaultTestLoader.loadTestsFromTestCase(ChoiceMechanismTestCase)
    suite.addTest(choice_test)
    whalrus_test = unittest.defaultTestLoader.loadTestsFromTestCase(WhalrusWrapperTestCase)
    suite.addTest(whalrus_test)
    greedy_test = unittest.defaultTestLoader.loadTestsFromTestCase(GreedySublistTestCase)
    suite.addTest(greedy_test)
    far_test = unittest.defaultTestLoader.loadTestsFromTestCase(FARTestCase)
    suite.addTest(far_test)
    ctx_test = unittest.defaultTestLoader.loadTestsFromTestCase(ContextClassTestCase)
    suite.addTest(ctx_test)
    if_test = unittest.defaultTestLoader.loadTestsFromTestCase(ItemFeatureTestCase)
    suite.addTest(if_test)
    ud_test = unittest.defaultTestLoader.loadTestsFromTestCase(UserDataTestCase)
    suite.addTest(ud_test)
    rhist_tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestResultsHistory)
    suite.addTest(rhist_tests)
    shist_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ScrufHistoryTestCase)
    suite.addTest(shist_tests)
    hcoll_tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestHistoryCollection)
    suite.addTest(hcoll_tests)
    bcoll_tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestBallotCollection)
    suite.addTest(bcoll_tests)
    rlist_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ResultListTestCase)
    suite.addTest(rlist_tests)
    conf_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ConfigUtilTestCase)
    suite.addTest(conf_tests)
    score_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ScoreDictTestCase)
    suite.addTest(score_tests)
    post_tests = unittest.defaultTestLoader.loadTestsFromTestCase(PostProcessorTestCase)
    suite.addTest(post_tests)
    integration_tests = unittest.defaultTestLoader.loadTestsFromTestCase(ScrufIntegrationTestCase)
    suite.addTest(integration_tests)

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

