import whalrus
import importlib
from abc import abstractmethod
from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection, MismatchedWhalrusRuleError, UnknownWhalrusTiebreakError


class WhalrusWrapperMechanism (ChoiceMechanism):
    _PROPERTY_NAMES = ['whalrus_rule', 'recommender_weight', 'tie_breaker',
                       'ignore_weights']

    _LEGAL_MECHANISMS = []
    _LEGAL_TIEBREAKERS = []

    def __init__(self):
        super().__init__()
        self.whalrus_class = None
        self.tiebreak_class = None
        self.whalrus_rule: whalrus.Rule = None
        self.converter = None

    def __str__(self):
        return f"WhalrusMechanism: whalrus= {self.get_property('whalrus_class')} rec_weight = {self.get_property('recommender_weight')}"

    def setup(self, input_properties):
        super().setup(input_properties)
        self.whalrus_class = self.get_whalrus_mechanism()
        self.tiebreak_class = self.get_tie_breaker()
        self.ignore_weights = self.get_property('ignore_weights')
        self.converter = whalrus.ConverterBallotGeneral()

    def get_whalrus_mechanism(self):
        rule_name = self.get_property('whalrus_rule')
        if self.check_rule_type(rule_name):
            module = importlib.import_module('whalrus')
            return getattr(module, rule_name)
        else:
            raise MismatchedWhalrusRuleError(rule_name, self.__class__.__name__)

    def get_tie_breaker(self):
        tiebreak_property = self.get_property('tie_breaker')
        if tiebreak_property == 'None':
            return None
        tiebreak_name = 'Priority' + tiebreak_property
        if self.check_tiebreak_type(tiebreak_property):
            module = importlib.import_module('whalrus')
            return getattr(module, tiebreak_name)
        else:
            raise UnknownWhalrusTiebreakError(tiebreak_name)

    def check_rule_type(self, rule_name):
        return rule_name in self._LEGAL_MECHANISMS

    def check_tiebreak_type(self, tiebreak_name):
        return tiebreak_name in self._LEGAL_TIEBREAKERS

    @abstractmethod
    def unwrap_result(self, user, list_size):
        pass

    @abstractmethod
    def invoke_whalrus_rule(self, ballots, weights=None):
        pass

    def compute_choice(self, agents: AgentCollection, bcoll: BallotCollection, recommended_items: ResultList, list_size):
        if self.ignore_weights:
            bcoll.set_ballot('__rec', recommended_items, 1.0) # weight doesn't matter
            wballots, weights = self.wrap_ballots(bcoll)
            self.invoke_whalrus_rule(wballots, weights=None)
        else:
            rec_weight = float(self.get_property('recommender_weight'))
            bcoll.set_ballot('__rec', recommended_items, rec_weight)
            wballots, weights = self.wrap_ballots(bcoll)
            self.invoke_whalrus_rule(wballots, weights=weights)
        user = recommended_items.get_user()
        output = self.unwrap_result(user, list_size) # Should include trim

        return bcoll, output


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


# For score-based mechanisms
class WhalrusWrapperScoring (WhalrusWrapperMechanism):
    # These are the ones that inherit from RuleScoreNum
    _LEGAL_MECHANISMS = ['RuleApproval', 'RuleBorda', 'RuleBucklinByRounds',
                         'RuleBucklinInstant', 'RuleCopeland', 'RuleKApproval',
                         'RuleMajorityJudgment', 'RuleMaximin', 'RulePlurality',
                         'RuleRangeVoting', 'RuleRankedPairs', 'RuleSimplifiedDodgson',
                         'RuleVeto']

    _LEGAL_TIEBREAKERS = ['None']

    def invoke_whalrus_rule(self, ballots, weights=None):
        if weights is None:
            self.whalrus_rule = self.whalrus_class(ballots)
        else:
            self.whalrus_rule = self.whalrus_class(ballots, weights=weights)

    def unwrap_result(self, user, list_size):
        scores = self.whalrus_rule.scores_as_floats_
        triples_list = []
        for item, score in scores.items():
            triples_list.append((user, item, score))
        result_list = ResultList()
        result_list.setup(triples_list, presorted=False, trim=list_size)
        return result_list


# For mechanisms that don't return a score
class WhalrusWrapperOrdinal (WhalrusWrapperMechanism):
    # These are the ones that don't inherit from RuleScoreNum
    _LEGAL_MECHANISMS = ['RuleBaldwin', 'RuleBlack', 'RuleCondorcet', 'RuleCoombs',
                         'RuleIRV', 'RuleKimRoush', 'RuleNanson',
                         'RuleSchulze', 'RuleTwoRound']

    _LEGAL_TIEBREAKERS = ['Unambiguous', 'Abstain', 'Ascending', 'Descending', 'Random']

    def invoke_whalrus_rule(self, ballots, weights=None):
        if weights is None:
            self.whalrus_rule = self.whalrus_class(ballots, tie_break=self.tiebreak_class())
        else:
            self.whalrus_rule = self.whalrus_class(ballots, weights=weights,
                                               tie_break=self.tiebreak_class())

    # Score range is 0..length of list. This is also something we might want to make configurable
    # some kind of normalization.
    def unwrap_result(self, user, list_size):
        ordered_items = self.whalrus_rule.strict_order_
        ordinal_scores = reversed(range(0, len(ordered_items)))
        scored_items = zip(ordered_items, ordinal_scores)
        triples_list = []
        for item, score in scored_items:
            triples_list.append((user, item, score))
        result_list = ResultList()
        result_list.setup(triples_list, presorted=False, trim=list_size)
        return result_list


mechanism_specs = [("whalrus_scoring", WhalrusWrapperScoring),
                   ('whalrus_ordinal', WhalrusWrapperOrdinal)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)