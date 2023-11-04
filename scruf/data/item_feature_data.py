from scruf.util import is_valid_keys, get_path_from_keys, ConfigKeys, ensure_list, maybe_number
import csv
from collections import defaultdict
from icecream import ic

# Reads in item, feature, value triples.
# Allows lookup: what features does this item have? what items have this feature? etc.
# TODO: Broke item feature data. protected_feature should be binary
# Communicate with Amanda and Cassidy about this.

class ItemFeatureData:

    def __init__(self):
        self.known_features: dict = None
        self.feature_file = None
        # feature id -> dict mapping value -> set of items
        self.feature_value_index: dict = None
        # item id -> dict mapping feature -> value
        self.item_feature_index: dict = None
        # feature id -> set of items with protected values for it
        self.protected_item_index: dict = None

    def setup(self, config):
        self.feature_file = get_path_from_keys(ConfigKeys.FEATURE_FILENAME_KEYS, check_exists=True, config=config)

        self.load_item_features()

        self.known_features = {}
        self.setup_features(config['feature'])

        self.setup_indices()

    def setup_features(self, feature_config):
        for feature in feature_config.keys():
            feature_name = feature_config[feature]['name']
            column_name = feature_config[feature]['protected_feature']
            protected = 'protected_values' in feature_config[feature]
            if protected:
                vals = feature_config[feature]['protected_values']
            else:
                vals = None
            self.known_features[feature_name] = (column_name, vals)

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
            if vals is not None:
                protected_items = set()

                feature_dict = self.feature_value_index[feature_id]
                for val in ensure_list(vals):
                    items = feature_dict[val]
                    protected_items.update(items)

                self.protected_item_index[feature_name] = protected_items

    def is_protected(self, feature_name, item):
        return item in self.protected_item_index[feature_name]

    def get_sensitive_features(self):
        return list(self.protected_item_index.keys())

    def get_item_features(self, item):
        return self.item_feature_index[item]

    # This is needed for OFAIR.
    # we convert the feature vector ϕ® to a smoothed binary vector of dummy variables bi with one dimension
    # for each possible feature value.
    # We are going to treat this in a binary fashion where the only distinction is protected vs unprotected
    # value. If the value is missing or unprotected , we create a "~" feature and set its value to 1. We set
    # original (protected) feature to epsilon. If the value is protected, we set the feature value to 1 and
    # set the unprotected feature to epsilon.
    # TODO: Allow non-binary protected features
    def get_item_features_dummify(self, item, epsilon=0):
        dummified_features = {}
        item_features = self.get_item_features(item)
        for feature_name, entry in self.known_features.items():
            feature, prot_val = entry
            not_feature = f'~{feature}'
            # If the item has the feature
            if feature in item_features:
                val = item_features[feature]
                # If the feature is protected
                if prot_val is not None:
                    # And the item's value is protected: only handles binary values for now
                    if val == prot_val:
                        dummified_features[feature] = 1
                        dummified_features[not_feature] = epsilon
                        continue

            # Other cases: Unprotected value, uprotected feature, feature absent
            dummified_features[feature] = epsilon
            dummified_features[not_feature] = 1
        return dummified_features
