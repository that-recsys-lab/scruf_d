from .choice_scorer import ChoiceScorer, ChoiceScorerFactory
import scruf
import copy
from scruf.util import ResultList

# Requires knowing protected items
class FixedValueChoiceScorer(ChoiceScorer):

    # Need to get the value as a property
    # Need to get protected feature as a property
    _PROPERTY_NAMES = ['protected_score_value', 'protected_feature']

    def __init__(self):
        super().__init__()

    def __str__(self):
        prot_value = self.get_property('protected_score_value')
        prot_feature = self.get_property('protected_feature')
        return f"FixedValueChoiceScore: protected feature = {prot_feature} associated value {prot_value}"

    # For every item in the list
    #   check if it is in the protected feature set
    #   if so, replace the score with the score + value
    #  return the list.
    # List size is ignored.
    def score_choices(self, rec_list: ResultList, _, inplace=False) -> ResultList:
        if not inplace:
            result_list = copy.deepcopy(rec_list)
        else:
            result_list = rec_list

        if_data = scruf.Scruf.state.item_features
        delta = float(self.get_property('protected_score_value'))
        # Maybe should be just delta or zero.
        result_list.rescore(lambda entry: entry.score +
                                    (delta if if_data.is_protected(entry.item) else 0))
        return result_list


# Register the mechanisms created above
scorer_specs = [("fixed_value", FixedValueChoiceScorer)]

ChoiceScorerFactory.register_choice_scorers(scorer_specs)
