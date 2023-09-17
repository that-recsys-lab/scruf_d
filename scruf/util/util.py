import random
from scruf.util import UnknownCollapseParameterError

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

# Non-destructive
def keyed_delete(lst, item, key=None):
    if key is None:
        new_lst = lst.copy()
        new_lst.remove(item)
        return new_lst
    else:
        return [entry for entry in lst if not key(entry)==item]

