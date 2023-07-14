import pandas as pd
from scruf.util import get_path_from_keys
from .post_processor import PostProcessor, PostProcessorFactory
import scruf
from numpy import log2, NINF
from icecream import ic


# Basic post-processing creates a dataframe with the following structure
# time stamp | fairness score (per agent) | compatibility score (per agent) | recommender input | final output
# A multi-index is used to organize the different parts of the dataframe
class DefaultPostProcessor(PostProcessor):
    _PROPERTY_NAMES = ['filename']

    def __init__(self):
        super().__init__()
        self.dataframe = None

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(DefaultPostProcessor._PROPERTY_NAMES, names))

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
        dataframe_path = get_path_from_keys(['post', 'properties', 'filename'], scruf.get_config())
        ic(dataframe_path)
        self.dataframe.to_csv(dataframe_path)

    def process(self):
        self.load_history()
        self.history_to_dataframe()
        self.save_dataframe()


class NDCGPostProcessor(DefaultPostProcessor):

    # If threshold = "none", then
    _PROPERTY_NAMES = ['binary', 'threshold']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(NDCGPostProcessor._PROPERTY_NAMES, names))

    # calculate ndcg given a list of recommended and ideal scores
    @staticmethod
    def ndcg(scores1, scores2):
        idealdcg = 0.0
        recdcg = 0.0
        for index, val in enumerate(scores1):
            recdcg += (2 ** val - 1) / log2(index + 2)
        for index, val in enumerate(scores2):
            idealdcg += (2 ** val - 1) / log2(index + 2)
        return recdcg / idealdcg

    @staticmethod
    def substitute_scores(rec_list, result_list):
        score_dict = {entry[0]: entry[1] for entry in rec_list}
        rescored_results = [(entry[0], score_dict[entry[0]]) for entry in result_list]
        return rescored_results

    @staticmethod
    def results_to_ndcg(rec_list, result_list, length, threshold=NINF, binary=False):
        recommended = result_list[0:length]
        rec_rescore = NDCGPostProcessor.substitute_scores(rec_list, recommended)
        ideal = rec_list[0:length]
        if binary:
            rec_thresh = [1 if score > threshold else 0 for item, score in rec_rescore]
            ideal_thresh = [1 if score > threshold else 0 for item, score in ideal]
        else:
            rec_thresh = [score if score > threshold else 0 for item, score in rec_rescore]
            ideal_thresh = [score if score > threshold else 0 for item, score in ideal]

        return NDCGPostProcessor.ndcg(rec_thresh, ideal_thresh)

    def compute_ndcg_column(self):
        length = scruf.Scruf.state.output_list_size
        threshold_str = self.get_property('threshold')
        if threshold_str.casefold() == 'none'.casefold():
            threshold = NINF
        else:
            threshold = float(threshold_str)
        binary = self.get_property('binary').casefold() == 'true'

        self.dataframe['nDCG'] = \
            self.dataframe['Results'].apply(
                lambda row: NDCGPostProcessor.results_to_ndcg(row['In'], row['Out'], length,
                                                              threshold=threshold,
                                                              binary=binary), axis=1)

    def process(self):
        self.load_history()
        self.history_to_dataframe()
        self.compute_ndcg_column()
        self.save_dataframe()

# TODO:
# ExposureFairnessPostProcessor that adds overall fairness
# AgentFairnessPostProcessor that adds fairness based on agent definitions
# Ultimately
# make this more configurable with accuracy and fairness as plug-ins.

# Register the processors created above
processor_specs = [("default", DefaultPostProcessor),
                   ("ndcg", NDCGPostProcessor)]

PostProcessorFactory.register_post_processors(processor_specs)
