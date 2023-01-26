import json
import pathlib

from scruf.util import HistoryCollection, get_value_from_keys, check_key_lists, ConfigKeys, \
    get_working_dir_path
from .results_history import ResultsHistory


class ScrufHistory:

    CONFIG_ELEMENTS = [ConfigKeys.WORKING_PATH_KEYS, ConfigKeys.OUTPUT_PATH_KEYS, ConfigKeys.WINDOW_SIZE_KEYS]

    @classmethod
    def check_config(cls, config):
        if not check_key_lists(config, ScrufHistory.CONFIG_ELEMENTS):
            raise ConfigKeyMissingError(ScrufHistory.CONFIG_ELEMENTS)

    def __init__(self):
        self.allocation_history: HistoryCollection = None
        self.choice_history: HistoryCollection = None
        self.fairness_history: HistoryCollection = None
        self.recommendation_input_history: ResultsHistory = None
        self.recommendation_output_history: ResultsHistory = None
        self.working_dir: pathlib.Path = None
        self.history_file_name: str = None
        self._history_file = None

    def setup(self, config):
        ScrufHistory.check_config(config)

        self.working_dir = get_working_dir_path(config)
        self.history_file_name = get_value_from_keys(config, ConfigKeys.OUTPUT_PATH_KEYS)
        window_size = get_value_from_keys(config, ConfigKeys.WINDOW_SIZE_KEYS)

        self.allocation_history = HistoryCollection(window_size)
        self.choice_history = HistoryCollection(window_size)
        self.fairness_history = HistoryCollection(window_size)
        self.recommendation_input_history = ResultsHistory(window_size)
        self.recommendation_output_history = ResultsHistory(window_size)

        self._history_file = open(self.working_dir / self.history_file_name, 'xt')

    def write_current_state(self):
        # the unreranked recommendation list for the current user
        rec_input = self.recommendation_input_history.get_most_recent()
        current_time = self.recommendation_input_history.time
        current_user = rec_input.results[0].user
        # a dict of agent: weight
        alloc = self.allocation_history.get_most_recent()
        # a dict of agent: choice outputs
        choice = self.choice_history.get_most_recent()
        # a dict of agent: fairness metric values
        fairness = self.fairness_history.get_most_recent()
        # the reranked recommendation list for the current user
        rec_output = self.recommendation_output_history.get_most_recent()

        output_json = {
            'current_time': current_time,
            'current_user': current_user,
            'fairness_metrics': fairness,
            'allocation_weights': alloc,
            'rec_input': rec_input,
            'choice': choice,
            'rec_output': rec_output
        }

        json_str = json.dumps(output_json)
        self._history_file.write(json_str)
        self._history_file.write('\n')
        self._history_file.flush()

        # TODO: Close the history file
    def cleanup(self):
        if not self._history_file.closed:
            self._history_file.close()
