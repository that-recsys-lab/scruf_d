from scruf.util import HistoryCollection
from .results_history import ResultsHistory

class ScrufHistory:

    def __init__(self):
        self.allocation_history = HistoryCollection()
        self.choice_history = HistoryCollection()
        self.fairness_history = HistoryCollection()
        self.recommendation_input_history = ResultsHistory()
        self.recommendation_output_history = ResultsHistory()
        self.history_file = None

    # TODO: Setup should open the history file for writing
    def setup(self, config):
        # Pieces of the config file
        # path for the working directory: location['path']
        # name of the history file: output['results']
        pass

    # TODO: Should have method for updating each type of history

