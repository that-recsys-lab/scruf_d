
# Note: possibly destructive
def normalize_score_dict(score_dict: dict, inplace=False):
    if not inplace:
        score_dict = score_dict.copy()
    magnitude = sum(score_dict.values())
    if magnitude > 0:
        for key in score_dict.keys():
            score_dict[key] = score_dict[key] / magnitude

    return score_dict

# Collapse scores
# type = max or min
# Picks the max or min entry from a score_dict
# If all are at an extreme (max, extreme = 0), (min extreme = 1), then return 0 vector
# If multiple equal max or min values, choose randomly or first


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
