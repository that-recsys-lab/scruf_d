import toml
from scruf.history import ScrufHistory
from scruf.agent import AgentCollection
from scruf.allocation import AllocationMechanismFactory, AllocationMechanism
from scruf.choice import ChoiceMechanismFactory, ChoiceMechanism
from scruf.data import ItemFeatureData, UserArrivalData, BulkLoadedUserData, Context, ContextFactory
from scruf.util import get_value_from_keys
from icecream import ic


class Scruf:

    class ScrufState:
        def __init__(self, config):
            self.config: dict = config
            self.history: ScrufHistory = ScrufHistory()

            # Fairness agents
            self.agents: AgentCollection = AgentCollection()

            # Data sources
            self.user_data: UserArrivalData = BulkLoadedUserData()
            self.item_features: ItemFeatureData = ItemFeatureData()
            ctx = ContextFactory.create_context_class(get_value_from_keys(config, ['context', 'context_class']))
            self.context: Context = ctx

            # Mechanisms
            amech = AllocationMechanismFactory.create_allocation_mechanism(config['allocation_class'])
            self.allocation_mechanism: AllocationMechanism = amech
            cmech = ChoiceMechanismFactory.create_choice_mechanism(config['choice_class'])
            self.choice_mechanism: ChoiceMechanism = cmech

            # Parameters
            self.output_list_size: int = get_value_from_keys(config, ['parameters', 'list_size'])
            self.iterations: int = get_value_from_keys(config, ['parameters', 'iterations'])

    state = None

    def __init__(self, config):
        Scruf.state = Scruf.ScrufState(config)
        ic(toml.dumps(config))

    @staticmethod
    def setup_experiment():
        # Fairness agents
        Scruf.state.agents.setup(Scruf.state.config)
        # Data sources
        Scruf.state.user_data.setup(Scruf.state.config)
        Scruf.state.item_features.setup(Scruf.state.config)
        # Mechanisms
        Scruf.state.allocation_mechanism.setup(Scruf.state.config)
        Scruf.state.choice_mechanism.setup(Scruf.state.config)
        # Bookkeeping
        Scruf.state.history.setup(Scruf.state.config)

    def run_experiment(self):
        Scruf.setup_experiment()
        self.run_loop(iterations=Scruf.state.iterations)
        Scruf.cleanup_experiment(self)

    # Get next user
    # Calculate fairness and compatibility
    # Run allocation mechanism
    # Get recommendations
    # Run choice mechanism
    # Produce final recommendation list
    # Update the history log
    # Loop
    def run_loop(self, iterations=-1, restart=True):
        agents = Scruf.state.agents
        history = Scruf.state.history
        context = Scruf.state.context
        amech = Scruf.state.allocation_mechanism
        cmech = Scruf.state.choice_mechanism

        for user_info in Scruf.state.user_data.user_iterator(iterations, restart=restart):
            allocation = amech.compute_allocation_probabilities(agents, history, context)
            cmech.compute_choice(agents, allocation, user_info, Scruf.state.output_list_size)
            history.write_current_state()


    @staticmethod
    def cleanup_experiment(self):
        Scruf.state.history.cleanup()
