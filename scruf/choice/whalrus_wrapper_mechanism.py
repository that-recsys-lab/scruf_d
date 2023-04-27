import whalrus
import importlib
from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection

# Note: This version of the mechanism really only works with rules of type RuleScoreNum because we
# make use of the .scores_as_floats_ feature. Doing it more generally would be possible but the scores
# coming back would be hella artificial.

class WhalrusWrapperMechanism (ChoiceMechanism):
#    _PROPERTY_NAMES = ['whalrus_rule', 'whalrus_properties', 'recommender_weight']
    _PROPERTY_NAMES = ['whalrus_rule', 'recommender_weight']

    def __init__(self):
        super().__init__()
        self.whalrus_class = None
        self.whalrus_rule: whalrus.RuleScoreNum = None
        self.converter = None

    def __str__(self):
        return f"WhalrusMechanism: whalrus= {self.get_property('whalrus_class')} rec_weight = {self.get_property('recommender_weight')}"

    def setup(self, input_properties):
        super().setup(input_properties)
        self.whalrus_class = self.get_whalrus_mechanism()
        self.converter = whalrus.ConverterBallotGeneral()

    def compute_choice(self, agents: AgentCollection, bcoll: BallotCollection, recommended_items: ResultList, list_size):
        rec_weight = float(self.get_property('recommender_weight'))
        bcoll.set_ballot('__rec', recommended_items, rec_weight)
        wballots, weights = self.wrap_ballots(bcoll)
        self.invoke_whalrus_rule(wballots, weights)
        user = recommended_items.get_user()
        output = self.unwrap_result(user, list) # Should include trim

        return bcoll, output

    def get_whalrus_mechanism(self):
        rule_name = self.get_property('whalrus_rule')
        module = importlib.import_module('whalrus')
        return getattr(module, rule_name)

    # SCRUF ballots are name, weight, result list (ordered <user, item, score> triples)
    # WHALRUS ballot objects can be created from an {item: score} dictionary. The agent weights have to be collected
    # separately, so this function returns ([ballots], [weights])
    def wrap_ballots(self, bcoll):
        wballot_list = []
        weight_list = []
        for ballot in bcoll.get_ballots():
            ballot_dict = {entry.item:entry.score for entry in ballot.prefs.get_results()}
            wballot = self.converter(ballot_dict)
            weight = ballot.weight
            wballot_list.append(wballot)
            weight_list.append(weight)
        return wballot_list, weight_list

    def invoke_whalrus_rule(self, ballots, weights):
        self.whalrus_rule = self.whalrus_class(ballots, weights=weights)

    def unwrap_result(self, user, list_size):
        scores = self.whalrus_rule.scores_as_floats_
        triples_list = []
        for item, score in scores.items():
            triples_list.append((user, item, score))
        result_list = ResultList()
        result_list.setup(triples_list, presorted=False, trim=list_size)
        return result_list


mechanism_specs = [("whalrus", WhalrusWrapperMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)