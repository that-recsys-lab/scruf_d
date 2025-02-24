import numpy as np
import scruf  # Access Scruf's history

# Dictionary to store fairness scores per agent
fairness_scores = {"tail": [], "female": []}
rbo_scores = []


def compute_diff(metrics):
    """
    Computes fairness and RBO differences based on the provided metrics.

    :param metrics: Dictionary containing fairness and RBO evaluation data.
    """
    history = scruf.Scruf.state.history
    agents = scruf.Scruf.state.agents

    # Compute fairness difference using ballot-based measurement
    if "fairness" in metrics:
        agent_ballots, results_list = metrics["fairness"]
        fairness_diff = compute_fairness_difference(agent_ballots, results_list)
        fairness_diff_agents = get_agents_fairness(agents, history)

        # Store fairness scores based on item overlap
        for agent, score in fairness_diff.items():
            fairness_scores[agent].append(score)

        print("Average Fairness Scores (last 50 interactions):")
        for agent, scores in fairness_scores.items():
            avg_score = np.mean(scores[-50:]) if len(scores) > 50 else np.mean(scores)
            print(f"Agent {agent} normalized presense score: {avg_score:.4f}")

        # Store fairness scores based on agent-computed fairness
        for agent, score in fairness_diff_agents.items():
            fairness_scores[agent].append(score)
            print(f"Agent {agent} fairness score: {fairness_scores[agent][-1]}")

    # Compute RBO difference
    if "rbo" in metrics:
        original_recommendations, modified_results = metrics["rbo"]
        rbo_diff = compute_rbo_difference(original_recommendations, modified_results)
        rbo_scores.append(rbo_diff)

    avg_rbo = np.mean(rbo_scores[-50:]) if len(rbo_scores) > 50 else np.mean(rbo_scores)
    print(f"Average RBO Score (last 50 interactions): {avg_rbo:.4f}")
    print("----------------------")


def compute_fairness_difference(agent_ballots, results):
    """
    Computes fairness difference by counting how many items from agent ballots appear in the final ranked list.

    :param agent_ballots: BallotCollection object containing ballots from different agents.
    :param results: ResultList object containing final ranked items.
    :return: Dictionary mapping agents to their computed fairness scores.
    """
    fairness_diff = {"tail": 0, "female": 0}
    result_items = {entry.item for entry in results.get_results()}

    for ballot in agent_ballots.get_ballots():
        agent_name = ballot.name.lower()
        if agent_name in fairness_diff:
            agent_items = {entry.item for entry in ballot.prefs.get_results()}
            fairness_count = len(agent_items & result_items)
            fairness_diff[agent_name] = fairness_count / max(1, len(agent_items))

    return fairness_diff


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


def compute_rbo_difference(original_list, modified_list, p=0.9):
    """
    Computes the Ranked Biased Overlap (RBO) difference between two ranked lists.

    :param original_list: Initial recommended list before fairness re-ranking.
    :param modified_list: List after applying fairness mechanisms.
    :param p: Persistence parameter, where higher values give more weight to top rankings.
    :return: RBO difference score (higher means greater ranking difference).
    """

    def rbo_score(S, L, p=0.9):
        S, L = (S, L) if len(S) <= len(L) else (L, S)
        overlap, rbo_sum = 0.0, 0.0
        for d in range(1, len(S) + 1):
            overlap += len(set(S[:d]) & set(L[:d])) / d
            rbo_sum += (overlap / d) * (p ** (d - 1))
        return (1 - p) * rbo_sum

    original_ranked_items = [entry.item for entry in original_list.get_results()]
    modified_ranked_items = [entry.item for entry in modified_list.get_results()]
    rbo_similarity = rbo_score(original_ranked_items, modified_ranked_items, p)

    return 1 - rbo_similarity
