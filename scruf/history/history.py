import jsons
import pathlib
import scruf
import os
from pyarrow import csv, parquet

from scruf.util import (
    HistoryCollection,
    get_value_from_keys,
    check_key_lists,
    ConfigKeys,
    get_working_dir_path,
    ConfigKeyMissingError,
)
from .results_history import ResultsHistory


class ScrufHistory:

    CONFIG_ELEMENTS = [
        ConfigKeys.WORKING_PATH_KEYS,
        ConfigKeys.OUTPUT_PATH_KEYS,
        ConfigKeys.WINDOW_SIZE_KEYS,
    ]

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
        self.working_dir: pathlib.Path = None
        self.history_file_name: str = None
        self._history_file = None

    def setup(self, config):
        ScrufHistory.check_config(config)

        self.working_dir = get_working_dir_path(config)
        self.history_file_name = get_value_from_keys(
            ConfigKeys.OUTPUT_PATH_KEYS, config
        )
        window_size = get_value_from_keys(ConfigKeys.WINDOW_SIZE_KEYS, config)

        self.allocation_history = HistoryCollection(window_size)
        self.choice_input_history = HistoryCollection(window_size)
        self.choice_output_history = HistoryCollection(window_size)

        # self.recommendation_input_history = ResultsHistory(window_size)
        # self.recommendation_output_history = ResultsHistory(window_size)


        history_path = self.working_dir / self.history_file_name
        if get_value_from_keys(["location", "overwrite"], config) == "true":
            if history_path.exists():
                history_path.unlink()

        self._history_file = open(history_path, "xt")

    def write_current_state(self):
        current_time = scruf.Scruf.state.user_data.current_user_index
        current_user = scruf.Scruf.state.user_data.get_current_user()
        alloc = self.allocation_history.get_most_recent()
        choice_input = self.choice_input_history.get_most_recent()
        choice_output = self.choice_output_history.get_most_recent()

        # agent-level outputs
        for agent in alloc["fairness scores"].keys():
            fair_output = [
                current_time,
                current_user,
                "agent",
                agent,
                alloc["fairness scores"][agent],
                "NaN",
                "fairness",
            ]

            if (
                alloc["compatibility scores"][agent]
                != alloc["compatibility scores"][agent]
            ):
                compat_score = "NaN"
            else:
                compat_score = alloc["compatibility scores"][agent]
            compat_output = [
                current_time,
                current_user,
                "agent",
                agent,
                compat_score,
                "NaN",
                "compatibility",
            ]
            alloc_output = [
                current_time,
                current_user,
                "agent",
                agent,
                alloc["output"][agent],
                "NaN",
                "allocation",
            ]

            fair_output = [str(item) for item in fair_output]
            compat_output = [str(item) for item in compat_output]
            alloc_output = [str(item) for item in alloc_output]

            self._history_file.write(", ".join(fair_output) + "\n")
            self._history_file.write(", ".join(compat_output) + "\n")
            self._history_file.write(", ".join(alloc_output) + "\n")

        # item-level outputs
        for entry in choice_input.ballots["__rec"].prefs.results:
            item = entry.item
            rank = entry.rank
            score = entry.score

            output = [current_time, current_user, "item", item, score, rank, "__rec"]

            output = [str(item) for item in output]
            self._history_file.write(", ".join(output) + "\n")

        for entry in choice_output.results:
            item = entry.item
            rank = entry.rank
            score = entry.score

            output = [current_time, current_user, "item", item, score, rank, "output"]
            output = [str(item) for item in output]
            self._history_file.write(", ".join(output) + "\n")

        self._history_file.flush()

    def cleanup(self, no_compress=False):
        if not self._history_file.closed:
            self._history_file.close()
        if no_compress:
            return
        table = csv.read_csv(str(self.working_dir) + "/" + self.history_file_name)
        parquet.write_table(
            table,
            str(self.working_dir)
            + "/"
            + os.path.splitext(self.history_file_name)[0]
            + ".parquet",
        )
        os.remove(str(self.working_dir) + "/" + self.history_file_name)
