import jsons
import pathlib
import scruf

from scruf.util import HistoryCollection, get_value_from_keys, check_key_lists, ConfigKeys, \
    get_working_dir_path, ConfigKeyMissingError
from .results_history import ResultsHistory


class ScrufHistory:

    CONFIG_ELEMENTS = [ConfigKeys.WORKING_PATH_KEYS, ConfigKeys.OUTPUT_PATH_KEYS, ConfigKeys.WINDOW_SIZE_KEYS]

    @classmethod
    def check_config(cls, config):
        if not check_key_lists(ScrufHistory.CONFIG_ELEMENTS, config):
            raise ConfigKeyMissingError(ScrufHistory.CONFIG_ELEMENTS)

    def __init__(self):
        self.allocation_history: HistoryCollection = None
        self.choice_input_history: HistoryCollection = None
        self.choice_output_history: HistoryCollection = None
        self.fairness_history: HistoryCollection = None
        self.recommendation_input_history: ResultsHistory = None
        self.recommendation_output_history: ResultsHistory = None
        self.click_history: ResultsHistory = None
        self.working_dir: pathlib.Path = None
        self.history_file_name: str = None
        self._history_file = None

    def setup(self, config):
        ScrufHistory.check_config(config)

        self.working_dir = get_working_dir_path(config)
        self.history_file_name = get_value_from_keys(ConfigKeys.OUTPUT_PATH_KEYS, config)
        window_size = get_value_from_keys(ConfigKeys.WINDOW_SIZE_KEYS, config)

        self.allocation_history = HistoryCollection(window_size)
        self.choice_input_history = HistoryCollection(window_size)
        self.choice_output_history = HistoryCollection(window_size)
        self.click_history = HistoryCollection(window_size)
        #self.recommendation_input_history = ResultsHistory(window_size)
        #self.recommendation_output_history = ResultsHistory(window_size)

        history_path = self.working_dir / self.history_file_name
        if get_value_from_keys(['location', 'overwrite'], config) == 'true':
            if history_path.exists():
                history_path.unlink()

        self._history_file = open(history_path, 'xt')

    def write_current_state(self):
        current_time = scruf.Scruf.state.user_data.current_user_index
        current_user = scruf.Scruf.state.user_data.get_current_user()
        alloc = self.allocation_history.get_most_recent()
        choice_input = self.choice_input_history.get_most_recent()
        choice_output = self.choice_output_history.get_most_recent()
        click = self.click_history.get_most_recent()

        output_json = {
            'time': current_time,
            'user': current_user,
            'allocation': alloc,
            'choice_in': choice_input,
            'choice_out': choice_output,
            'click': click
        }

        json_str = jsons.dumps(output_json)
        self._history_file.write(json_str)
        self._history_file.write('\n')
        self._history_file.flush()

        # TODO: Close the history file
    def cleanup(self):
        if not self._history_file.closed:
            self._history_file.close()
