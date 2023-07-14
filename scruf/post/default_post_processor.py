import pandas as pd
from scruf.util import get_path_from_keys
from .post_processor import PostProcessor, PostProcessorFactory
import scruf
from icecream import ic


# Basic post-processing creates a dataframe with the following structure
# time stamp | fairness score (per agent) | compatibility score (per agent) | recommender input | final output
# A multi-index is used to organize the different parts of the dataframe
class DefaultPostProcessor(PostProcessor):
    _PROPERTY_NAMES = ['filename']

    def __init__(self):
        super().__init__()
        self.dataframe = None

    def history_to_dataframe(self):
        # Fairness scores
        fair_list = list(self.entry_iterate(['allocation', 'fairness scores']))
        fair_df = pd.DataFrame(fair_list)

        # Compatibility scores
        compat_list = list(self.entry_iterate(['allocation', 'compatibility scores']))
        compat_df = pd.DataFrame(compat_list)

        # Allocation distribution
        alloc_list = list(self.entry_iterate(['allocation', 'output']))
        alloc_df = pd.DataFrame(alloc_list)
        alloc_df['none'] = (compat_df.sum(axis=1) == 0).astype(int)

        # Input and output
        ballot_in = [self.process_results(results)
                     for results in self.entry_iterate(['choice_in','ballots','__rec','prefs','results'])]

        results_out = [self.process_results(results)
                       for results in self.entry_iterate(['choice_out','results'])]
        results_df = pd.DataFrame({'In': ballot_in, 'Out': results_out})

        self.dataframe = pd.concat([fair_df, compat_df, alloc_df, results_df], axis=1,
                               keys=['Fairness', 'Compatibility', 'Allocation', 'Results'])

    def save_dataframe(self):
        dataframe_path = get_path_from_keys(['post', 'properties', 'filename'], scruf.Scruf.state.config)
        ic(dataframe_path)
        self.dataframe.to_csv(dataframe_path)


    def process(self):
        self.load_history()
        self.history_to_dataframe()
        self.save_dataframe()


# TODO:
# NDCGPostProcessor that adds the NDCG calculation
# ExposureFairnessPostProcessor that adds overall fairness
# AgentFairnessPostProcessor that adds fairness based on agent definitions
# Ultimately
# make this more configurable with accuracy and fairness as plug-ins.

# Register the processors created above
processor_specs = [("default", DefaultPostProcessor)]

PostProcessorFactory.register_post_processors(processor_specs)
