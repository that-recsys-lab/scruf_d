import toml
from history import ScrufHistory
from agent import AgentCollection
from icecream import ic

class Scruf:

    def __init__(self, config):
        self.config = config
        ic(toml.dumps(config))
        self.history = ScrufHistory()
        self.agents = AgentCollection()
        self.allocation_mechanism = None
        self.choice_mechanism = None

    def run_experiment(self):
        self.setup_experiment()
        self.run_loop()
        self.cleanup_experiment()

    def setup_experiment(self):
        # TODO Setup data sources
        self.history.setup(self.config)
        self.agents.setup(self.config)
        # TODO Setup allocation mechanism
        # TODO Setup choice mechanism

    def run_loop(self):
        pass

    def cleanup_experiment(self):
        self.history.cleanup()