import numpy as np
import scruf  # Access Scruf's history
import rbo


# Dictionary to store fairness scores per agent
class rl_scores:
    def __init__(self):
        self.fairness_scores = {"tail": [], "female": []}
        self.rbo_scores = []


mab_scores = rl_scores()


def fairness_rbo_diff(metrics):
    """
    Computes fairness and RBO differences based on the provided metrics.

    :param metrics: Dictionary containing fairness and RBO evaluation data.
    """
    history = scruf.Scruf.state.history
    agents = scruf.Scruf.state.agents

    fairness_results = {}  # Dictionary to store fairness scores per agent
    rbo_result = None  # Variable to store RBO difference

    # Compute fairness difference using ballot-based measurement
    if "fairness" in metrics:
        # get assigned agents names
        original_recommendations, modified_results = metrics["fairness"]
        assigned_agents = get_assigned_agents_names(original_recommendations)

        # Computes fairness scores based on history (last 50 items) by calling the compute_fairness method for each fairness agent.
        fairness_diff_agents = get_agents_fairness(agents, history)

        # Store fairness scores based on agent-computed fairness
        for agent, score in fairness_diff_agents.items():
            mab_scores.fairness_scores[agent].append(score)
            fairness_results[agent] = {"score": score}

    # Compute RBO difference
    if "rbo" in metrics:
        original_recommendations, modified_results = metrics["rbo"]
        rbo_diff = compute_rbo_difference(original_recommendations, modified_results)
        mab_scores.rbo_scores.append(rbo_diff)

        # Compute average RBO score
        avg_rbo = (
            np.mean(mab_scores.rbo_scores[-50:])
            if len(mab_scores.rbo_scores) > 50
            else np.mean(mab_scores.rbo_scores)
        )
        rbo_result = {"score": rbo_diff, "average": avg_rbo}

    return {"assigned_agents": assigned_agents, "fairness": fairness_results, "rbo": rbo_result}


def get_assigned_agents_names(agent_ballots):
    """
    Returns the names of the fairness agents.

    :return: List of assigned agents names.
    """
    assigned_agents = []
    for ballot in agent_ballots.get_ballots():
        assigned_agents.append(ballot.name.lower())
    return assigned_agents


def compute_rbo_difference(original_list, modified_list):
    """
    Computes the Ranked Biased Overlap (RBO) difference between two ranked lists.

    :param original_list: Initial recommended list before fairness re-ranking.
    :param modified_list: List after applying fairness mechanisms.
    :return: RBO difference score (higher means greater ranking difference).
    """

    original_ranked_items = [int(entry.item) for entry in original_list.get_results()][
        : len(modified_list.get_results())
    ]
    modified_ranked_items = [int(entry.item) for entry in modified_list.get_results()]

    rbo_similarity = rbo.RankingSimilarity(
        original_ranked_items, modified_ranked_items
    ).rbo()

    return rbo_similarity


def get_agents_fairness(agents, history):
    """
    Computes fairness scores by calling the compute_fairness method for each fairness agent.

    :param agents: List of fairness agents.
    :param history: ScrufHistory object containing historic interactions.
    :return: Dictionary mapping agents to their computed fairness scores.
    """
    fairness_diff = {"tail": 0, "female": 0}
    for agent in fairness_diff.keys():
        agent_instance = agents.get_agent(agent)
        if agent_instance:
            fairness_diff[agent] = agent_instance.compute_fairness(history)

    return fairness_diff

# def compute_fairness_difference(agent_ballots, results):
#     """
#     Computes fairness difference by counting how many items from agent ballots appear in the final ranked list.

#     :param agent_ballots: BallotCollection object containing ballots from different agents.
#     :param results: ResultList object containing final ranked items.
#     :return: Dictionary mapping agents to their computed fairness scores.
#     """
#     fairness_diff = {"tail": 0, "female": 0}
#     result_items = {entry.item for entry in results.get_results()}

#     for ballot in agent_ballots.get_ballots():
#         agent_name = ballot.name.lower()
#         if agent_name in fairness_diff:
#             agent_items = {entry.item for entry in ballot.prefs.get_results()}
#             fairness_count = len(agent_items & result_items)
#             fairness_diff[agent_name] = fairness_count / max(1, len(agent_items))

#     return fairness_diff
