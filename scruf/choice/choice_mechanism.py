import copy
from abc import ABC, abstractmethod
import random
from scruf.agent import AgentCollection
from scruf.util import (
    BallotCollection,
    InvalidChoiceMechanismError,
    UnregisteredChoiceMechanismError,
    ResultList,
    PropertyMixin,
)
import scruf
from icecream import ic

# RL Updates
import logging
import json
from scruf.scruf_rl.fairness_rbo_diff import fairness_rbo_diff
from scruf.scruf_rl.usb_mob import UCBMultiObjectiveBandit
import numpy as np

rl_logger = logging.getLogger("rl_logger")
rl_logger.setLevel(logging.INFO)
if not rl_logger.handlers:
    handler = logging.FileHandler("rl_scores.log", mode="a")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    rl_logger.addHandler(handler)

lambdas = np.arange(0.5, 2.1, 0.2).tolist()
bandit = UCBMultiObjectiveBandit(lambdas, logger=rl_logger)
# End of RL Updats


class ChoiceMechanism(PropertyMixin, ABC):
    """
    A ChoiceMechanism takes in a list of weights, a list of agents, a list of recommended items. The agents generate
    their own preference lists and the specific compute_choice method combines the weights and the preferences.
    """

    def setup(self, input_props, names=None):
        super().setup(input_props, names=names)

    # TODO: It would be better to copy the recommender ballot into bcoll here and save to the history,
    # rather than rely on compute_choice not to alter it.
    def do_choice(self, allocation_probabilities, recommendations: ResultList):
        agents = scruf.Scruf.state.agents
        list_size = scruf.Scruf.state.output_list_size
        agent_ballots = self.compute_agent_ballots(
            agents, allocation_probabilities, recommendations
        )

        # SELECT rec_weight from bandit
        selected_lambda, selected_index = bandit.select_lambda()

        # Use the selected rec_weight for choice
        bcoll, results = self.rl_compute_choice(
            agents,
            agent_ballots,
            recommendations,
            list_size,
            rec_weight=selected_lambda,
        )

        # Log history
        scruf.Scruf.state.history.choice_input_history.add_item(bcoll)
        scruf.Scruf.state.history.choice_output_history.add_item(results)

        #  Compute fairness & RBO scores
        rl_scores = fairness_rbo_diff(
            {"fairness": [agent_ballots, results], "rbo": [recommendations, results]}
        )

        # UPDATE the bandit with the observed reward and log values
        bandit.update(selected_index, rl_scores)

        return results

    def compute_agent_ballots(
        self, agents, allocation_probabilities, recommendations: ResultList
    ):
        bcoll = BallotCollection()
        for agent_name, prob in allocation_probabilities.items():
            if prob > 0:
                aobj = agents.get_agent(agent_name)
                prefs = aobj.compute_preferences(recommendations)
                bcoll.set_ballot(agent_name, prefs, prob)
        return bcoll

    @abstractmethod
    # Returns the ballots (including the recommender) and the final result
    def compute_choice(
        self,
        agents: AgentCollection,
        bcoll: BallotCollection,
        recommendations: ResultList,
        list_size,
    ):
        pass


class NullChoiceMechanism(ChoiceMechanism):
    """
    The agents have no influence on the recommendations
    """

    def __init__(self):
        super().__init__()

    def compute_choice(
        self,
        agents,
        ignore_bcoll: BallotCollection,
        recommended_items: ResultList,
        list_size,
    ):
        """
        Returns the recommendation list without any re-ranking.
        :return: selected agent for each user
        """
        bcoll = BallotCollection()
        recommended_items.sort()
        bcoll.set_ballot(BallotCollection.REC_NAME, recommended_items, 1.0)
        output = copy.deepcopy(recommended_items)
        output.trim(list_size)
        return bcoll, output


class ChoiceMechanismFactory:
    """
    A factory class for creating ChoiceMechanism objects.
    """

    _choice_mechanisms = {}

    @classmethod
    def register_choice_mechanism(cls, mechanism_type, mechanism_class):
        if not issubclass(mechanism_class, ChoiceMechanism):
            raise InvalidChoiceMechanismError(mechanism_class)
        cls._choice_mechanisms[mechanism_type] = mechanism_class

    @classmethod
    def register_choice_mechanisms(cls, mechanism_specs):
        for mechanism_type, mechanism_class in mechanism_specs:
            cls.register_choice_mechanism(mechanism_type, mechanism_class)

    @classmethod
    def create_choice_mechanism(cls, mechanism_type):
        mechanism_class = cls._choice_mechanisms.get(mechanism_type)
        if mechanism_class is None:
            raise UnregisteredChoiceMechanismError(mechanism_type)
        return mechanism_class()


# Register the mechanisms created above
mechanism_specs = [("null_choice", NullChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)
