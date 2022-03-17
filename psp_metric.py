import argparse
import numpy as np
import math
from librec_auto.core.util.protected_feature import ProtectedFeature

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd
from pathlib import Path
from librec_auto.core.util.xml_utils import single_xpath
import pandas as pd

def load_item_features(config, data_path):
    item_feature_file = single_xpath(
        config.get_xml(), '/librec-auto/features/item-feature-file').text
    item_feature_path = data_path / item_feature_file

    if not item_feature_path.exists():
        print("Cannot locate item features. Path: " + item_feature_path)
        return None

    item_feature_df = pd.read_csv(item_feature_path,
                                  names=['itemid', 'feature', 'value'])
    item_feature_df.set_index('itemid', inplace=True)
    return item_feature_df


class PSPMetric(ListBasedMetric):
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        super().__init__(params, conf, test_data, result_data, output_file)

        temp_directory = config.get_files().get_temp_dir_path()
        protected_feats = ProtectedFeature(ProtectedFeature.parse_protected(config), temp_dir=temp_directory)

        # 03-16-22 The feature is binary. The question is it new? rather than what is the condition?
        protected_item_value = protected_feats.lookup("fea:new")["column"]

        data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text
        data_path = Path(data_dir)
        data_path = data_path.resolve()

        item_feature_df = load_item_features(config, data_path)

        mask = item_feature_df["feature"] == protected_item_value

        self._protected_item_ids = item_feature_df[mask].index.values

        self._name = 'PSP'

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:

        result_df = pd.DataFrame(result_user_data, columns=["userID", "itemID", "rating"])

        mask = result_df["itemID"].isin(self._protected_item_ids)
        protected_result_data = result_df[mask]

        protected_num = protected_result_data.shape[0]
        total_num = result_df.shape[0]
        protected_num_ratio = protected_num / total_num

        return(protected_num_ratio - (1 - protected_num_ratio))



    def postprocessing(self):
        return np.average(self._values)

def read_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='My custom metric')
    parser.add_argument('--conf', help='Path to config file')
    parser.add_argument('--test', help='Path to test.')
    parser.add_argument('--result', help='Path to results.')
    parser.add_argument('--output-file', help='The output pickle file.')

    # Custom params defined in the config go here
    parser.add_argument('--list_size', help='Size of the list for PSP.')

    input_args = parser.parse_args()
    print(vars(input_args))
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    # parse_protected
    # protected_feature_file can be parsed here
    config = read_config_file(args['conf'], '.')


    params = {'list_size': args['list_size']}

    test_data = ListBasedMetric.read_data_from_file(
        args['test']
    )
    result_data = ListBasedMetric.read_data_from_file(
        args['result'],
        delimiter=','
    )

    print("Creating metric")

    custom = PSPMetric({}, config, test_data, result_data,
                                    args['output_file'])

    print("Applying metric")
    custom.evaluate()