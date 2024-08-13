import random

import scruf
from scruf.history import ScrufHistory
from scruf.agent import AgentCollection
from scruf.allocation import AllocationMechanismFactory, AllocationMechanism
from scruf.choice import ChoiceMechanismFactory, ChoiceMechanism
from scruf.post import PostProcessorFactory, PostProcessor
from scruf.data import ItemFeatureData, UserArrivalData, BulkLoadedUserData, Context, ContextFactory
from scruf.util import get_value_from_keys, is_valid_keys, check_key_lists, get_working_dir_path, get_path_from_keys
from icecream import ic
from tqdm import tqdm


class Scruf:

    class ScrufState:
        def __init__(self, config):
            if config is not None:
                self.config: dict = config
                self.rand = random.Random(get_value_from_keys(['parameters', 'random_seed'], config, default=420))
                self.history: ScrufHistory = ScrufHistory()

                # Fairness agents
                self.agents: AgentCollection = AgentCollection()

                # Data sources
                self.user_data: UserArrivalData = BulkLoadedUserData()
                self.item_features: ItemFeatureData = ItemFeatureData()

                ctx_class = get_value_from_keys(['context', 'context_class'], config)
                ctx = ContextFactory.create_context_class(ctx_class)
                self.context: Context = ctx

                # Mechanisms
                amech_class = get_value_from_keys(['allocation', 'allocation_class'], config)
                amech = AllocationMechanismFactory.create_allocation_mechanism(amech_class)
                self.allocation_mechanism: AllocationMechanism = amech

                cmech_class = get_value_from_keys(['choice', 'choice_class'], config)
                cmech = ChoiceMechanismFactory.create_choice_mechanism(cmech_class)
                self.choice_mechanism: ChoiceMechanism = cmech

                # Post-processing
                post_class = get_value_from_keys(['post', 'postprocess_class'], config)
                post = PostProcessorFactory.create_post_processor(post_class)
                self.post_processor: PostProcessor = post

                # Parameters
                self.output_list_size: int = get_value_from_keys(['parameters', 'list_size'], config)
                self.iterations: int = get_value_from_keys(['parameters', 'iterations'], config)

    state: ScrufState = None

    # post_only flag is currently ignored but could be used to avoid some setup tasks.
    def __init__(self, config, post_only=False):
        Scruf.state = Scruf.ScrufState(config)

    @staticmethod
    def setup_experiment():
        # Fairness agents
        Scruf.state.agents.setup(Scruf.state.config)
        # Data sources
        Scruf.state.user_data.setup(Scruf.state.config)
        Scruf.state.item_features.setup(Scruf.state.config)
        Scruf.state.context.setup(Scruf.state.config)
        # Mechanisms
        amech_props = Scruf.get_value_from_keys(['allocation', 'properties'], default={})
        Scruf.state.allocation_mechanism.setup(amech_props)
        cmech_props = Scruf.get_value_from_keys(['choice', 'properties'], default={})
        Scruf.state.choice_mechanism.setup(cmech_props)
        # Post processing
        post_props = Scruf.get_value_from_keys(['post', 'properties'], default={})
        Scruf.state.post_processor.setup(post_props)
        # Bookkeeping
        Scruf.state.history.setup(Scruf.state.config)

    def run_experiment(self, progress=False):
        Scruf.setup_experiment()
        self.run_loop(iterations=Scruf.state.iterations, progress=progress)
        Scruf.cleanup_experiment()
        Scruf.post_process()

    # Get next user
    # Calculate fairness and compatibility
    # Run allocation mechanism
    # Get recommendations
    # Run choice mechanism
    # Produce final recommendation list
    # Update the history log
    # Loop
    def run_loop(self, iterations=-1, restart=True, progress=False):
        agents = Scruf.state.agents
        history = Scruf.state.history
        context = Scruf.state.context
        amech = Scruf.state.allocation_mechanism
        cmech = Scruf.state.choice_mechanism


        if progress:
            user_data = tqdm(Scruf.state.user_data.user_iterator(iterations, restart=restart))
        else:
            user_data = Scruf.state.user_data.user_iterator(iterations, restart=restart)

        for user_info in user_data:
            allocation = amech.do_allocation(user_info)
            cmech.do_choice(allocation, user_info)
            history.write_current_state()



    @staticmethod
    def cleanup_experiment():
        Scruf.state.history.cleanup()

    @staticmethod
    def post_process():
        # Post processing needs setup
        post_props = Scruf.get_value_from_keys(['post', 'properties'], default={})
        Scruf.state.post_processor.setup(post_props)
        # Also need item features
        Scruf.state.item_features.setup(Scruf.state.config)
        # Do the evaluation
        Scruf.state.post_processor.process()

    @staticmethod
    def is_valid_keys(key_list):
        return is_valid_keys(key_list, Scruf.state.config)

    @staticmethod
    def get_value_from_keys(key_list, default=None):
        return get_value_from_keys(key_list, Scruf.state.config, default=default)

    @staticmethod
    def check_key_lists(path_specs):
        return check_key_lists(path_specs, Scruf.state.config)

    @staticmethod
    def get_working_dir_path():
        return get_working_dir_path(Scruf.state.config)

    @staticmethod
    def get_path_from_keys(keys, check_exists=False):
        return get_path_from_keys(keys, Scruf.state.config, check_exists=check_exists)

def get_config():
    return scruf.Scruf.state.config

def get_state():
    return scruf.Scruf.state