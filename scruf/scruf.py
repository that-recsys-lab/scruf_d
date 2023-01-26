import toml
from scruf.history import ScrufHistory
from scruf.agent import AgentCollection
from scruf.allocation import AllocationMechanismFactory
from scruf.choice import ChoiceMechanismFactory
from scruf.data import ItemFeatureData
from icecream import ic

class Scruf:

    class ScrufState:
        def __init__(self, config):
            self.config = config
            self.history = ScrufHistory()
            self.agents = AgentCollection()
            self.item_features = ItemFeatureData()
            amech = AllocationMechanismFactory.create_allocation_mechanism(config['allocation_class'])
            self.allocation_mechanism = amech
            cmech = ChoiceMechanismFactory.create_choice_mechanism(config['choice_class'])
            self.choice_mechanism = cmech

    state = None

    def __init__(self, config):
        Scruf.state = Scruf.ScrufState(config)
        ic(toml.dumps(config))

    def setup_experiment(self):
        # Fairness agents
        Scruf.state.agents.setup(Scruf.state.config)
        # Data sources
        Scruf.state.item_features.setup(Scruf.state.config)
        # Mechanisms
        Scruf.state.allocation_mechanism.setup(Scruf.state.config)
        Scruf.state.choice_mechanism.setup(Scruf.state.config)
        # Bookkeeping
        Scruf.state.history.setup(Scruf.state.config)

    def run_experiment(self):
        self.setup_experiment()
        self.run_loop()
        self.cleanup_experiment()

    # Get next user
    # Calculate fairness and compatibility
    # Run allocation mechanism
    # Get recommendations
    # Run choice mechanism
    # Produce final recommendation list
    # Update the history log
    # Loop
    def run_loop(self):
        pass

    def cleanup_experiment(self):
        Scruf.state.history.cleanup()
