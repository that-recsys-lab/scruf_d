# The data that feeds the simulation.
# Encapsulates a file of the following form:
# userID, itemID, rating
# All rows are grouped by userID and there should be the same number of rows for each user.
# Later on, we might want a streaming method
from abc import ABC, abstractmethod
from scruf.util import get_path_from_keys, get_value_from_keys, ConfigKeys, InputListLengthError
import csv
from scruf.util import ResultList, ResultEntry
from collections import defaultdict
import scruf
from icecream import ic

class UserArrivalData(ABC):

    @abstractmethod
    def setup(self, config):
        pass

    @abstractmethod
    def user_iterator(self, iterations=-1, restart=True):
        pass


class BulkLoadedUserData(UserArrivalData):

    def __init__(self):
        self.data_file = None
        self.current_user_index = -1
        self.arrival_sequence = None
        self.user_table = None

    def __str__(self):
        return f"UserArrivalData: currentUser = {self.arrival_sequence[self.current_user_index]}"

    def setup(self, config):
        self.data_file = get_path_from_keys(ConfigKeys.DATA_FILENAME_KEYS, config, check_exists=True)
        self._load_data()
        self.data_check(config)

    def _load_data(self):
        self.arrival_sequence = []
        self.user_table = defaultdict()
        last_user_id = None
        current_user_collect = []
        with open(self.data_file, 'r') as csvfile:
            reader = csv.reader(csvfile, skipinitialspace=True)
            for row in reader:
                user_id = row[0]
                if last_user_id != user_id: # On to the next user
                    if last_user_id is not None:  # Not the first user
                        rlist = ResultList()
                        rlist.setup(current_user_collect)
                        self.user_table[last_user_id] = rlist
                        self.arrival_sequence.append(last_user_id)
                    # Always reset
                    current_user_collect = []
                    last_user_id = user_id

                current_user_collect.append(row)
        # Need to assemble last result list
        rlist = ResultList()
        rlist.setup(current_user_collect)
        self.user_table[last_user_id] = rlist
        self.arrival_sequence.append(last_user_id)

        self.current_user_index = None

    def data_check(self, config):
        user = self.arrival_sequence[0]
        user_data: ResultList = self.user_table[user]
        rec_list_len = len(user_data.get_results())
        output_list_len = get_value_from_keys(['parameters', 'list_size'], config)
        if rec_list_len <= output_list_len:
            raise InputListLengthError(rec_list_len, output_list_len)

    # Default is to go through all users
    # NOT THREAD SAFE. Assumes only one iteration happening at a time
    # Also assumes that the data does not change during the iteration
    def user_iterator(self, iterations=-1, restart=True):
        if restart:
            self.current_user_index = -1

        if iterations == -1 or iterations > len(self.arrival_sequence):
            last_item_read = len(self.arrival_sequence) - 1
        elif self.current_user_index == -1:
            last_item_read = iterations - 1
        else:
            last_item_read = self.current_user_index + iterations

        # ic("creating iterator", self.current_user_index, iterations, last_item_read, restart)

        while self.current_user_index < last_item_read:
            self.current_user_index += 1
            arrived_user = self.get_current_user()
            yield self.user_table[arrived_user]

    def get_current_user(self):
        return self.arrival_sequence[self.current_user_index]
