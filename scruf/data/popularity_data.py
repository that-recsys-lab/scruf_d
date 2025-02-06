from abc import ABC, abstractmethod
from collections import defaultdict
from scruf.util import PropertyMixin, InvalidContextClassError, UnregisteredContextClassError, get_path_from_keys
import csv



class LoadPopularityData:

    def __init__(self):
        self.data_file = None
        self.popularity_dict = {}

    def setup(self, config):
        # Get the file path from the config and ensure it exists
        self.data_file = get_path_from_keys(['context', 'properties', 'popularity_data'], config, check_exists=True)
        self._load_data()

    def _load_data(self):
        # Read the CSV file and populate the popularity dictionary
        with open(self.data_file, "r") as f:
            reader = csv.DictReader(f, fieldnames=['item_id', 'popularity'])
            for row in reader:
                item_id = row['item_id']
                popularity = float(row['popularity'])  # Convert popularity to float if needed
                self.popularity_dict[item_id] = popularity


class CSVTest(Test):
    _PROPERTY_NAMES = ["test_data"]

    def __init__(self):
        super().__init__()
        self.test_dict = defaultdict(dict)

    def setup(self, config, names=None):
        super().setup(config['context']['properties'],
                      names=self.configure_names(CSVTest._PROPERTY_NAMES, names))
        test_data = get_path_from_keys(['context', 'properties', 'test_data'], config,
                                       check_exists=True)

        with open(test_data, "r") as f:
            reader = csv.DictReader(f, fieldnames=['item_id', 'popularity'])
            for row in reader:
                item_id = row['item_id']
                popularity = row['popularity']
                self.popularity_dict[item_id] = popularity

    def get_test(self, user_id):
        return self.test_dict[user_id]


class ContextFactory:
    """
    The ContextFactory associates names with class objects so these can be instantiated
    based on configuration information. A context class must registered in the factory before it can be
    created. Note these are all class methods, so an instance of this object never needs to be created.
    """

    _context_classes = {}

    @classmethod
    def register_context_class(cls, context_type, context_class):
        if not issubclass(context_class, Context):
            raise InvalidContextClassError(context_class)
        cls._context_classes[context_type] = context_class

    @classmethod
    def register_context_classes(cls, context_specs):
        for context_type, context_class in context_specs:
            cls.register_context_class(context_type, context_class)

    @classmethod
    def create_context_class(cls, context_type):
        context_class = cls._context_classes.get(context_type)
        if context_class is None:
            raise UnregisteredContextClassError(context_type)
        return context_class()


# Register the context classes created above
context_specs = [("null_context", NullContext), ("csv_context", CSVContext), ("popularity", LoadPopularityData)]

ContextFactory.register_context_classes(context_specs)
