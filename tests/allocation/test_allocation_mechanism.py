import unittest
import toml
import random
import scruf
from icecream import ic

from scruf.agent import AgentCollection, BinaryPreferenceFunction
from scruf.allocation import AllocationMechanismFactory, WeightedProductAllocationMechanism, \
    MostCompatibleAllocationMechanism, LeastFairAllocationMechanism, StaticAllocationLottery

SAMPLE_PROPERTIES = '''
[allocation]
algorithm = "weighted_product_allocation"
[allocation.properties]
fairness_exponent = 1.0
compatibility_exponent = 0.7
'''

SAMPLE_AGENTS = '''
[agent]

[agent.low_compat]
name = "Low Compatibility"
metric_class = "always_zero"
compatibility_class = "always_zero"
preference_function_class = "binary_preference"

[agent.low_compat.preference]
feature = "foo"
delta = 0.5

[agent.high_compat]
name = "High Compatibility"
metric_class = "always_one"
compatibility_class = "always_one"
preference_function_class = "binary_preference"

[agent.high_compat.preference]
feature = "bar"
delta = 0.5
'''

SAMPLE_AGENTS2 = '''
[agent]

[agent.a_compat]
name = "A Compatibility"
metric_class = "always_zero"
compatibility_class = "always_one"
preference_function_class = "binary_preference"

[agent.a_compat.preference]
feature = "foo"
delta = 0.5

[agent.b_compat]
name = "B Compatibility"
metric_class = "always_zero"
compatibility_class = "always_one"
preference_function_class = "binary_preference"

[agent.b_compat.preference]
feature = "bar"
delta = 0.5
'''

SAMPLE_AGENTS3 = '''
[agent]

[agent.a_compat]
name = "A Compatibility"
metric_class = "always_zero"
compatibility_class = "always_zero"
preference_function_class = "binary_preference"

[agent.a_compat.preference]
feature = "foo"
delta = 0.5

[agent.b_compat]
name = "B Compatibility"
metric_class = "always_zero"
compatibility_class = "always_zero"
preference_function_class = "binary_preference"

[agent.b_compat.preference]
feature = "bar"
delta = 0.5
'''

SAMPLE_LOTTERY_PROPERTIES = '''
[allocation]
algorithm = "static_lottery"
[allocation.properties]
weights = [["Agent 1", "0.5"], ["Agent 2", "0.2"]]
'''

SAMPLE_LOTTERY_PROPERTIES2 = '''
[allocation]
algorithm = "product_lottery"
'''

SAMPLE_LOTTERY_PROPERTIES3 = '''
[allocation]
algorithm = "weighted_product_lottery"
[allocation.properties]
fairness_exponent = 0.0
compatibility_exponent = 0.0
'''

SAMPLE_LOTTERY_PROPERTIES4 = '''
[allocation]
algorithm = "fairness_lottery"
'''

SAMPLE_LOTTERY_PROPERTIES5 = '''
[allocation]
algorithm = "product_allocation"
'''

SAMPLE_LOTTERY_PROPERTIES6 = '''
[allocation]
algorithm = "weighted_product_allocation"
[allocation.properties]
fairness_exponent = 0.0
compatibility_exponent = 0.0
'''

class AllocationMechanismTestCase(unittest.TestCase):

    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup(config['allocation']['properties'])

        self.assertEqual(alloc.__class__, WeightedProductAllocationMechanism)
        self.assertAlmostEqual(alloc.get_property('compatibility_exponent'), 0.7)

    def test_mechanism_scoring(self):
        config = toml.loads(SAMPLE_AGENTS)
        agents = AgentCollection()
        agents.setup(config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.rand = random.Random(20220223)

        alloc1 = MostCompatibleAllocationMechanism()
        alloc1.setup({})

        alloc_result = alloc1.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        self.assertEqual(probs1['Low Compatibility'], 0.0)
        self.assertEqual(probs1['High Compatibility'], 1.0)

        alloc2 = LeastFairAllocationMechanism()
        alloc2.setup({})

        alloc_result = alloc2.compute_allocation_probabilities(agents, None, None)
        probs2 = alloc_result['output']

        self.assertEqual(probs2['Low Compatibility'], 1.0)
        self.assertEqual(probs2['High Compatibility'], 0.0)

    def test_static_lottery(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup(config['allocation']['properties'])
        lottery = alloc.lottery
        self.assertEqual(lottery['Agent 1'], 0.5)
        self.assertEqual(lottery['Agent 2'], 0.2)
        self.assertAlmostEqual(lottery['__dummy__'], 0.3)

    def test_product_lottery(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES2)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup({})

        agent_config = toml.loads(SAMPLE_AGENTS2)
        agents = AgentCollection()
        agents.setup(agent_config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.rand = random.Random(20220223)
        scruf.Scruf.state.agents = agents

        alloc_result = alloc.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        # With this random seed, the scores should be 0, 1
        probA = probs1['A Compatibility']
        probB = probs1['B Compatibility']

        self.assertAlmostEqual(probA, 0.0, 4)
        self.assertAlmostEqual(probB, 1.0, 4)


    def test_weighted_product_lottery(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES3)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup(config['allocation']['properties'])

        agent_config = toml.loads(SAMPLE_AGENTS3)
        agents = AgentCollection()
        agents.setup(agent_config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.rand = random.Random(20220223)
        scruf.Scruf.state.agents = agents

        alloc_result = alloc.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        compatibilityB = alloc_result['compatibility scores']['B Compatibility']

        probA = probs1['A Compatibility']
        probB = probs1['B Compatibility']

        self.assertAlmostEqual(compatibilityB, 0.0, 4)
        self.assertAlmostEqual(probA, 0.0, 4)
        self.assertAlmostEqual(probB, 1.0, 4) # Only possible if the exponent is applied

    def test_fairness_lottery(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES4)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup({})

        agent_config = toml.loads(SAMPLE_AGENTS3)
        agents = AgentCollection()
        agents.setup(agent_config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.rand = random.Random(20220223)
        scruf.Scruf.state.agents = agents

        alloc_result = alloc.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        # With this random seed, the scores should be 0, 1
        probA = probs1['A Compatibility']
        probB = probs1['B Compatibility']

        self.assertAlmostEqual(probA, 0.0, 4)
        self.assertAlmostEqual(probB, 1.0, 4)

    def test_product_allocation(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES5)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup({})

        agent_config = toml.loads(SAMPLE_AGENTS2)
        agents = AgentCollection()
        agents.setup(agent_config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.agents = agents

        alloc_result = alloc.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        probA = probs1['A Compatibility']
        probB = probs1['B Compatibility']

        # equally allocated
        self.assertAlmostEqual(probA, 0.5, 4)
        self.assertAlmostEqual(probB, 0.5, 4)

    def test_weighted_product_allocation(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES6)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup(config['allocation']['properties'])

        agent_config = toml.loads(SAMPLE_AGENTS3)
        agents = AgentCollection()
        agents.setup(agent_config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.agents = agents

        alloc_result = alloc.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        compatibilityB = alloc_result['compatibility scores']['B Compatibility']

        probA = probs1['A Compatibility']
        probB = probs1['B Compatibility']

        self.assertAlmostEqual(compatibilityB, 0.0, 4)
        self.assertAlmostEqual(probA, 0.5, 4)
        self.assertAlmostEqual(probB, 0.5, 4) # Only possible if the exponent is applied

