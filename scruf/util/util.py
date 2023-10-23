import random
from .errors import UnknownCollapseParameterError

# Note: possibly destructive
def normalize_score_dict(score_dict: dict, inplace=False):
    if not inplace:
        score_dict = score_dict.copy()
    magnitude = sum(score_dict.values())
    if magnitude > 0:
        for key in score_dict.keys():
            score_dict[key] = score_dict[key] / magnitude
    else:
        for key in score_dict.keys():
            score_dict[key] = 0

    return score_dict


# Collapse scores
# type = max or min
# Picks the max or min entry from a score_dict
# If all are at an extreme (max, extreme = 0), (min extreme = 1), then return None
# If multiple equal max or min values, choose randomly or first
def collapse_score_dict(score_dict: dict, type='max', handle_multiple='first', rand=random.Random()):
    if type == 'max' and all([score == 0.0 for score in score_dict.values()]):
        return None

    if type == 'min' and all([score == 1.0 for score in score_dict.values()]):
        return None

    if type == 'max':
        selected_value = max(score_dict.values())
    elif type == 'min':
        selected_value = min(score_dict.values())
    else:
        raise UnknownCollapseParameterError('type', type)

    items_at_value = [key for key, val in score_dict.items() if val == selected_value]

    if handle_multiple == 'first':
        return items_at_value[0]
    if handle_multiple == 'random':
        return rand.choice(items_at_value)
    else:
        raise UnknownCollapseParameterError('handle_multiple', handle_multiple)


def ensure_list(val):
    if type(val) is not list:
        return [val]
    else:
        return val


def maybe_number(s):
    try:
        fl = float(s)
        return fl
    except ValueError:
        return s

####
# Some functions for handling dictionaries treated as feature vectors.
####


# Element-by-element multiplication of two dictionaries
# Returns another such dictionary
def dict_vector_multiply(dict1: dict, dict2: dict):
    output = dict()
    keys1 = list(dict1.keys())
    keys2 = list(dict2.keys())
    if len(keys1) != len(keys2):
        raise KeyError(f'Mismatched keys in {dict1} and {dict2}')

    for key, val in dict1.items():
        if key not in dict2:
            raise KeyError(f'Feature {key} missing in {dict2}')
        else:
            output[key] = val * dict2[key]
    return output


def dict_vector_dot(dict1: dict, dict2: dict):
    output = 0
    keys1 = list(dict1.keys())
    keys2 = list(dict2.keys())
    if len(keys1) != len(keys2):
        raise KeyError(f'Mismatched keys in {dict1} and {dict2}')

    for key, val in dict1.items():
        if key not in dict2:
            raise KeyError(f'Feature {key} missing in {dict2}')
        else:
            output += val * dict2[key]

    return output


def dict_vector_scale(factor, dict1: dict):
    output = dict()
    keys1 = list(dict1.keys())

    for key, val in dict1.items():
        output[key] = val * factor
    return output
