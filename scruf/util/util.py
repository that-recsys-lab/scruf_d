
# Note: destructive
def normalize_score_dict(score_dict: dict, inplace=False):
    if not inplace:
        score_dict = score_dict.copy()
    magnitude = sum(dict.values())
    for key in score_dict.keys():
        score_dict[key] = score_dict[key] / magnitude

    return score_dict