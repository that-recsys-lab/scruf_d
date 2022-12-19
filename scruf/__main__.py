import argparse
import logging
import os
import toml
from .util.errors import ConfigFileError

def read_args():
    parser = argparse.ArgumentParser(
        description='SCRUF-D tool for dynamic fairness-aware recommender systems experiments')

    parser.add_argument('config', help='Path to the configuration file.')

    input_args = parser.parse_args()
    arg_check(vars(input_args))
    return vars(input_args)

def arg_check(input_args):
    config_file = input_args['config']
    if not os.path.exists(config_file):
        print(f'Configuration file {config_file} not found. Working directory: {os.getcwd()} Exiting.')
        exit(-1)
    else:
        return

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = toml.load(f)
    return config

if __name__ == '__main__':

    args = read_args()
    config = load_config(args['config_file'])

    if config == None:
        raise ConfigFileError(args['config_file'])

    scruf = Scruf(config)

    scruf.run_experiment()

    exit(0)