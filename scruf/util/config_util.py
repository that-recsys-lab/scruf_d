# Utilities for working with the TOML input
from scruf.util.errors import ConfigKeyMissingError


def is_valid_keys(config, key_list):
    if len(key_list) == 0:
        return True
    else:
        head_key = key_list[0]
        if head_key in config:
            return is_valid_keys(config[head_key], key_list[1:])
        else:
            return False


def get_value_from_keys(config, key_list, default=None):
    if len(key_list) == 0:
        return config
    else:
        head_key = key_list[0]
        if head_key in config:
            return get_value_from_keys(config[head_key], key_list[1:])
        elif default is None:
            raise ConfigKeyMissingError(head_key)
        else:
            return default


def check_keys(config, path_specs):
    return all(map(lambda path: is_valid_keys(config, path), path_specs))