
# Note: destructive
def normalize_score_dict(score_dict: dict, inplace=False):
    if not inplace:
        score_dict = score_dict.copy()
    magnitude = sum(dict.values())
    for key in score_dict.keys():
        score_dict[key] = score_dict[key] / magnitude

    return score_dict


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
