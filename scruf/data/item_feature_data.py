from scruf.util import is_valid_keys, get_path_from_keys, ConfigKeys, ensure_list, maybe_number
import csv
from collections import defaultdict

# Reads in item, feature, value triples.
# Allows lookup: what features does this item have? what items have this feature? etc.


class ItemFeatureData:

    def __init__(self):
        self.known_features = None
        self.feature_file = None
        # feature id -> dict mapping value -> set of items
        self.feature_value_index = None
        # item id -> dict mapping feature -> value
        self.item_feature_index = None
        # feature id -> set of items with protected values for it
        self.protected_item_index = None

    def setup(self, config):
        self.feature_file = get_path_from_keys(config, ConfigKeys.FEATURE_FILENAME_KEYS, check_exists=True)

        self.load_item_features()

        self.known_features = {}
        if is_valid_keys(config, ['feature']):
            self.setup_features(config['feature'])

        self.setup_indices()

    def setup_features(self, feature_config):
        for feature in feature_config.keys():
            feature_name = feature_config[feature]['name']
            protected = feature_config[feature]['protected_feature']
            vals = feature_config[feature]['protected_values']
            self.known_features[feature_name] = (protected, vals)

    # Item features in triple format: item id, feature name, value
    def load_item_features(self):
        self.item_feature_index = defaultdict(dict)
        with open(self.feature_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['item', 'feature', 'value'],
                                    skipinitialspace=True)
            for row in reader:
                feature_value = maybe_number(row['value'])
                self.item_feature_index[row['item']][row['feature']] = feature_value

    def setup_indices(self):
        # Map from features and their values to the items that have those values
        self.feature_value_index = defaultdict(lambda: defaultdict(set))
        for item_id, item_dict in self.item_feature_index.items():
            for feature, value in item_dict.items():
                self.feature_value_index[feature][value].add(item_id)

        self.protected_item_index = {}
        for feature_name, entry in self.known_features.items():
            feature_id, vals = entry
            protected_items = set()

            feature_dict = self.feature_value_index[feature_id]
            for val in ensure_list(vals):
                items = feature_dict[val]
                protected_items.update(items)

            self.protected_item_index[feature_name] = protected_items
