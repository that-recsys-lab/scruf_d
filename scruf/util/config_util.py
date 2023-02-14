# Utilities for working with the TOML input
from scruf.util.errors import ConfigKeyMissingError, PathDoesNotExistError
import scruf
from pathlib import Path

class ConfigKeys:
    WORKING_PATH_KEYS = ['location', 'path']
    FEATURE_FILENAME_KEYS = ['data', 'feature_filename']
    OUTPUT_PATH_KEYS = ['output', 'filename']
    WINDOW_SIZE_KEYS = ['parameters', 'history_window_size']
    DATA_FILENAME_KEYS = ['data', 'rec_filename']


def is_valid_keys(key_list, config):
    if len(key_list) == 0:
        return True
    else:
        head_key = key_list[0]
        if head_key in config:
            return is_valid_keys(key_list[1:], config=config[head_key])
        else:
            return False


def get_value_from_keys(key_list, config, default=None):
    if len(key_list) == 0:
        return config
    else:
        head_key = key_list[0]
        if head_key in config:
            return get_value_from_keys(key_list[1:], config[head_key], default=default)
        elif default is None:
            raise ConfigKeyMissingError(head_key)
        else:
            return default


def check_key_lists(path_specs, config):
    return all(map(lambda path: is_valid_keys(path, config), path_specs))


def get_working_dir_path(config):
    return Path(get_value_from_keys(ConfigKeys.WORKING_PATH_KEYS, config)).absolute()


def get_path_from_keys(keys, config, check_exists=False):
    working_dir = get_working_dir_path(config)
    relative_dir = get_value_from_keys(keys, config)
    full_path = working_dir / relative_dir
    if check_exists:
        if full_path.exists():
            return full_path
        else:
            raise PathDoesNotExistError(full_path, keys)
