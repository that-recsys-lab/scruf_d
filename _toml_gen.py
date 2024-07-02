import toml
import numpy as np
import pandas as pd
import pathlib
from ruamel.yaml import YAML

yaml = YAML(typ="safe")
params = yaml.load(open("../scruf-dvc-experiments/params.yaml", encoding="utf-8"))

folder_path = params["config"]["folder_path"]

base_toml = params["config"]["base_toml"]
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def generate_config(base, config_number, rec_weight, choice, allocation, filename_suffix):
    base_toml = toml.load(base)
    new_filename = remove_suffix(base_toml["output"]["filename"], ".json") + f"_{filename_suffix}_{config_number}.json"
    base_toml["output"]["filename"] = new_filename
    # Check if the choice is "weighted_scoring"
    if choice == "weighted_scoring":
        base_toml["choice"]["choice_class"] = choice
    else:
        base_toml["choice"]["properties"]["whalrus_rule"] = choice
        base_toml["choice"]["properties"]["tie_breaker"] = "Random"
        base_toml["choice"]["properties"]["ignore_weights"] = "false"
        base_toml["choice"]['choice_class'] = "whalrus_scoring"
    base_toml["allocation"]["allocation_class"] = allocation
    if allocation == "weighted_product_allocation":
        base_toml["allocation"]["properties"]["compatibility_exponent"] = 2
        base_toml["allocation"]["properties"]["fairness_exponent"] = 1
    base_toml["choice"]["properties"]["recommender_weight"] = rec_weight


    name = f"{folder_path}/{remove_suffix(base.split('/')[-1], '.toml')}_{filename_suffix}_{config_number}.toml"
    with open(name, 'w') as f:
        toml.dump(base_toml, f)
    return name, new_filename



config_number_counter = 0
path_list = []

choices = params['config']['choice']
allocations = params['config']['allocation']
rec_weights = params['config']['rec_weight']

for choice in choices:
    for allocation in allocations:
        for rec_weight in rec_weights:
            config_number_counter += 1
            toml_name, history_name = generate_config(base_toml, config_number_counter, float(rec_weight),
                                                      choice, allocation, f"{choice}_{allocation}")
            path_list.append((config_number_counter, toml_name, history_name, float(rec_weight)))

config_df = pd.DataFrame(path_list, columns=['Config Number', 'Config Path', 'Output Path', 'recommender_weight'])
config_df.to_csv(f"{folder_path}/path_list.csv")