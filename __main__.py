import argparse
import logging
import os
import toml
import yaml
from yaml import Loader
from scruf.util.errors import ConfigFileError
from scruf import Scruf


def read_args():
    parser = argparse.ArgumentParser(
        description="SCRUF-D tool for dynamic fairness-aware recommender systems experiments"
    )

    parser.add_argument("config_file", help="Path to the configuration file.")
    parser.add_argument(
        "-p",
        "--post",
        action="store_true",
        help="Post-processing only. If set, no simulation will be run.",
    )
    parser.add_argument(
        "-g", "--progress", action="store_true", help="Shows progress bar if set."
    )
    parser.add_argument(
        "-dnc",
        "--do_not_compress",
        action="store_true",
        help="Disables automatic parquet compression of history files.",
    )

    input_args = parser.parse_args()
    arg_check(vars(input_args))
    return vars(input_args)


def arg_check(input_args):
    config_file = input_args["config_file"]
    if not os.path.exists(config_file):
        print(
            f"Configuration file {config_file} not found. Working directory: {os.getcwd()} Exiting."
        )
        exit(-1)
    else:
        return


def load_config(config_file):
    with open(config_file, "r") as f:
        if config_file.lower().endswith(".toml"):
            config = toml.load(f)
        elif config_file.lower().endswith((".yaml", ".yml")):
            config = yaml.load(f, Loader=Loader)
    return config


if __name__ == "__main__":

    args = read_args()
    config = load_config(args["config_file"])
    post_only = args["post"]
    progress = args["progress"]

    if config == None:
        raise ConfigFileError(args["config_file"])

    scruf = Scruf(config, post_only=post_only)

    if post_only:
        scruf.post_process()

    scruf.run_experiment(progress=progress, compress=args["do_not_compress"])

    exit(0)
