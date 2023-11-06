from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection, Ballot, \
    dict_vector_dot, dict_vector_multiply, dict_vector_scale
from scruf.data import ItemFeatureData, Context
from collections import defaultdict
from copy import copy
from abc import abstractmethod
import numpy as np
from .greedy_sublist_choice import GreedySublistChoiceMechanism, MMRAbstractChoiceMechanism
import scruf

# See Weiwen Liu, Jun Guo, Nasim Sonboli, Robin Burke,and Shengyu Zhang.
# 2019. Personalized Fairness-aware Re-ranking for Microlending. In Thirteenth
# ACM Conference on Recommender Systems (RecSys’19).
# https://doi.org/10.1145/3298689.3347016
# max_{v∈R(u)} (1 − λ)P(v|u) + λ sum_c P(V_c)I_{v∈V_c} prod_{i∈S(u)}I_{i not in Vc}
# For borrower-side fairness, our idea is to promote the loans that belong to currently uncovered
# borrower groups. For a loan v that belongs to Vc, we first compute the coverage of Vc for the current
# generated re-ranked list S(u) as prod_{i∈S(u)} I{i not in Vc}, which is equal to 1 if none of the items
# in S(u) belong to Vc, and 0 otherwise. If both I{v ∈Vc } and prod_{i∈S(u)} I{i not in Vc } are 1, items
# that belong to Vc are promoted by being assigned a higher score, and thus get a larger chance of being
# selected. The above process is repeated for each borrower group Vc , c = 1, ...,nc , and the results
# are summed up. Since each item may belong to multiple groups, the loans belonging to multiple uncovered
# borrower groups are favored. The normalization term P(Vc ) is determined by the system an indicates the
# importance of Vc . For example, if a borrower group is identified as a protected group and receives few
# recommendations, then the system can assign a higher P(Vc ) to the corresponding group. For simplicity,
# we assume a uniform preference over borrower groups and assign an equal P(Vc ) for all borrower groups.

# Note that the product term is the product of indicator functions so it is only 1 if all of the indicators
# are 1 meaning that none of the items in the recommendation list are protected per this ballot.
# We can use the allocation weight to be P(Vc).
# We use rec_weight as lambda elsewhere so the lambda definition will be reversed here.
# There is a non-binary version of FAR, which uses the fraction of protected items rather than the indicator
# function. Ideally, this would be list-wise fairness score from the agent, but that isn't a thing in SCRUF.
# We are sticking with proportional here as that is the original definition.

class FARChoiceMechanism(GreedySublistChoiceMechanism):
    _PROPERTY_NAMES = ['use_allocation_weight', 'binary']

    def __init__(self):
        super().__init__()
        self.feature_map = None

    def setup(self, input_props, names=None):
        super().setup(input_props,
                      names=self.configure_names(FARChoiceMechanism._PROPERTY_NAMES, names))

    def build_feature_map(self, ballots: BallotCollection):
        self.feature_map = defaultdict(set)
        for ballot in ballots.get_ballots():
            for entry in ballot.entry_iterator():
                if entry.score > 0:
                    self.feature_map[ballot.name].add(entry.item)

    # In the binary case, this is zero if any item in the results is protected
    # by the agent. In the non-binary case, this is 1 - the proportion of protected
    # items in the list. Really it should be a function that comes from the agent itself
    # but that isn't supported yet.
    # TODO: List-wise fairness scoring where possible.
    def representation_score(self, results: ResultList, agent):
        binary = self.get_property('binary') in {'True', 'true'}
        agent_item_set = self.feature_map[agent]
        count = 0
        agent_count = 0
        for item in results.result_item_iter():
            count += 1
            if item in agent_item_set:
                if binary:
                    return 0
                else:
                    agent_count += 1
        # If it's binary and we got this far, then there are no protected items
        if binary:
            return 1
        else:
            return 1 - (float(agent_count) / count)

    # I think we don't need this
    # @staticmethod
    # def get_agent_fairness(self, agent):
    #     agent_obj = scruf.Scruf.state.agents.get_agent(agent)
    #     return agent_obj.recent_fairness

    def filter_ballot(self, ballot: Ballot, candidates: ResultList):
        ballot.prefs = ballot.prefs.filter_results(
            lambda entry: candidates.contains_item(entry.item))

    # Destructive to ballots. Shouldn't matter because they are copied in parent class compute_choice
    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):

        rec_weight = ballots.get_ballot(BallotCollection.REC_NAME).weight
        self.build_feature_map(ballots)

        # For each fairness agent
        for ballot in ballots.get_ballots():
            # calculate prod_{i∈S(u)}I_{i not in Vc}
            if ballot.name != BallotCollection.REC_NAME:
                rep_score = self.representation_score(list_so_far, ballot.name)
                # drop votes for items already in the output list
                self.filter_ballot(ballot, candidates)
                # No sort because we're going to merge later
                ballot.prefs.rescore_no_sort(
                    lambda entry: rep_score * ballot.weight if entry.score > 0 else 0)

        scored = ballots.merge(candidates.get_user())
        return scored

# we personalize the previous re-ranking criterion Eq.(1) by
# adding a personalized weight τu and derive our Personalized Fairness-aware Re-ranking
# (PFAR)criterion Eq.(2).
# For any u ∈ U, we solve max v ∈R(u) (1 − λ)P(v|u) + λ τu sum_c P(V_c)I_{v∈V_c} prod_{i∈S(u)}I_{i not in Vc}
# where the second term considers personalized fairness. The diversity tolerance τu is incorporated
# to control the weight of the fairness score.

# The idea here is to look up the agent compatibility and then use that to re-weight the ballots. Note that
# the original paper uses overall compatibility, which is a sum over the feature-specific entropies. The
# compatibility is a scaled version of that.
# Again we will switch the definition of lambda to be consistent with the other definitions: lambda is the
# recommender weight.
# Does the non-binary definition make sense here? It will run that way but not sure that it should.
class PFARChoiceMechanism(FARChoiceMechanism):

    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):

        agents = scruf.Scruf.state.agents
        total_compatibility = 0
        for ballot in ballots.get_ballots():
            if not ballot.is_recommender():
                ballot_agent = agents.get_agent(ballot.name)
                total_compatibility += ballot_agent.recent_compatibility

        for ballot in ballots.get_ballots():
            if not ballot.is_recommender():
                ballot.weight *= total_compatibility

        return super().sublist_scorer(list_so_far, candidates, ballots)


# OFAiR borrows from MMR the idea of finding an item with maximum dissimilarity to the existing
# list but it does two things differently:
# * Instead of using Jaccard similarity, it uses weighted cosine
# * The weights come from the product of user tolerance / compatibility and a weighting function
# where unprotected features have score alpha/100 and protected features alpha. alpha was equal
# to 1 in the original experiments. Epsilon was ϵ = 2.2e−16
# MMR(u,v, R, S) △= arg max_{v∈R\S} [λ(rec(v,u) − (1 − λ) max_{v′∈S} sim(v,v′)]
# TODO: This does not work. Needs to access item representations, not just agent information.
class OFairChoiceMechanism(MMRAbstractChoiceMechanism):
    _PROPERTY_NAMES = ['alpha', 'epsilon', 'non_sensitive_discount']

    def __init__(self):
        super().__init__()
        self.alpha = None
        self.epsilon = None
        self.discount = None
        self.item_features : ItemFeatureData = None
        self.context : Context = None

    def setup(self, input_props, names=None):
        super().setup(input_props,
                      names=self.configure_names(OFairChoiceMechanism._PROPERTY_NAMES, names))
        self.alpha = float(self.get_property('alpha'))
        self.epsilon = float(self.get_property('epsilon'))
        self.discount = float(self.get_property('non_sensitive_discount'))
        # Just sugar to save some typing
        self.item_features = scruf.Scruf.state.item_features
        self.context = scruf.Scruf.state.context

    # Efficiency might require switching to a more vector-oriented representation.
    # Let's see if it's an issue.
    def ballot_weighted_cosine(self, item1, item2, weights):
        feature_vector1 = self.item_features.get_item_features_dummify(item1, self.epsilon)
        feature_vector2 = self.item_features.get_item_features_dummify(item2, self.epsilon)

        numer = dict_vector_dot(dict_vector_multiply(weights, feature_vector1), feature_vector2)
        wsq_len1 = dict_vector_dot(dict_vector_multiply(weights, feature_vector1), feature_vector1)
        wsq_len2 = dict_vector_dot(dict_vector_multiply(weights, feature_vector2), feature_vector2)
        denom = np.sqrt(wsq_len1 * wsq_len2)

        return numer / denom

    # Project the context into the dummy feature vector space
    def project_context(self, item, list_so_far: ResultList):
        projected_context = dict()
        user_id = list_so_far.get_user()
        for feature, val in self.context.get_context(user_id).items():
            projected_context[feature] = val
            projected_context[f'~{feature}'] = val
        return projected_context

    # Compatibility weights. This is a vector where the feature and ~feature entries are set to the
    # the entropy values for the associated features, if any. We can't get this from compatibility
    # because we need entropy for all features, not just sensitive ones.
    # Protected weights. This is a vector where the feature and ~feature entries are set to alpha for
    # sensitive VALUES or alpha/discount for non-sensitive values. (This is a bit unclear in the paper,
    # TBH but because values are supposed to == features in the dummified feature space, maybe this
    # is equivalent.)

    def max_similarity(self, item, list_so_far: ResultList):
        # tolerance weights are compatibility projected in the feature/~feature space
        tolerance_weights = self.project_context(item, list_so_far)
        protected_weights = self.item_features.get_item_features_dummify(item, 1/self.discount)
        protected_weights = dict_vector_scale(self.alpha, protected_weights)
        weights = dict_vector_multiply(protected_weights, tolerance_weights)
        cosines = [self.ballot_weighted_cosine(item, output_item, weights)
                    for output_item in list_so_far.result_item_iter()]
        return max(cosines)

    def candidates_vs_list_score(self, candidates, list_so_far):
        # For each candidate, score it based on sum of similarities with output items so far
        scored = copy(candidates)
        scored.rescore(lambda entry: self.max_similarity(entry.item, list_so_far))

        return scored

    # Have to have our own sublist scorer so that we can create the ballot weights.
    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):

        # Drop the recommender from the agents
        drop_rec = ballots.subset([BallotCollection.REC_NAME], copy=True, inverse=True)

        # Grab the weight
        rec_weight = ballots.get_ballot(BallotCollection.REC_NAME).weight

        scored = self.candidates_vs_list_score(candidates, list_so_far)
        rescored_ballots = BallotCollection()
        rescored_ballots.set_ballot('mmr', scored, -(1 - rec_weight))
        #ic(rescored_ballots.get_ballot('mmr'))

        # Add the recommender back in
        rescored_ballots.set_ballot(BallotCollection.REC_NAME, candidates, rec_weight)
        final_scoring = rescored_ballots.merge(candidates.get_user(), ignore_weight=False)
        #ic(final_scoring)
        return final_scoring

# Register the mechanisms created above
mechanism_specs = [("FAR", FARChoiceMechanism),
                   ("PFAR", PFARChoiceMechanism),
                   ("OFAIR", OFairChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)