import toml
from history import ScrufHistory
from agent import AgentCollection
from allocation import AllocationMechanismFactory
from choice import ChoiceMechanismFactory
from icecream import ic

class Scruf:

    def __init__(self, config):
        self.config = config
        ic(toml.dumps(config))
        self.history = ScrufHistory()
        self.agents = AgentCollection()
        self.allocation_mechanism = \
            AllocationMechanismFactory.create_allocation_mechanism(config['allocation_class'])
        self.choice_mechanism = \
            AllocationMechanismFactory.create_allocation_mechanism(config['allocation_class'])

    def setup_experiment(self):
        # TODO Setup data sources
        self.history.setup(self.config)
        self.agents.setup(self.config)
        self.allocation_mechanism.setup(self.config)
        self.choice_mechanism.setup(self.config)

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
        self.history.cleanup()