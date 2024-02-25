import argparse
import logging
import os
import toml
from scruf.util.errors import ConfigFileError
from scruf import Scruf
from _toml_gen import path_list
import pathlib

def read_args():
    parser = argparse.ArgumentParser(
        description='SCRUF-D tool for dynamic fairness-aware recommender systems experiments')

    parser.add_argument('config_file', help='Path to the configuration file.')

    input_args = parser.parse_args()
    arg_check(vars(input_args))
    return vars(input_args)


def arg_check(input_args):
    config_file = input_args['config_file']
    if not os.path.exists(config_file):
        print(f'Configuration file {config_file} not found. Working directory: {os.getcwd()} Exiting.')
        exit(-1)
    else:
        return


def load_config(config_file):
    with open(config_file, 'r') as f:
        config = toml.load(f)
    return config


config_paths = path_list
counter = 0
total = len(path_list)
for config_path in config_paths:
    counter += 1
    config = load_config(config_path[1])
    if config == None:
        raise ConfigFileError("No file found")
    scruf = Scruf(config)
    scruf.run_experiment()
    print("Finished: "+str(counter)+"/"+str(total))

#os.remove("fair1.toml")
#os.remove("fair2.toml")
exit(0)