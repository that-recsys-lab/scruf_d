import numpy as np
import json


class UCBMultiObjectiveBandit:
    """
    A multi-objective Upper Confidence Bound (UCB) bandit designed to dynamically select
    a recommender weighting parameter (lambda) that balances accuracy and fairness.

    Reward is computed as a weighted average between:
    - Accuracy: measured by the Ranked Biased Overlap (RBO) between the fairness-modified list
                and the original recommender list. Higher RBO = higher accuracy.
    - Fairness: computed as the harmonic mean between two fairness agent scores (e.g., 'tail' and 'female').

    A dynamic weighting factor alpha ∈ [0, 1] is computed at each step based on the relative
    variance (stability) of RBO and fairness scores:
        alpha = var(RBO) / (var(RBO) + var(Fairness))

    This makes the system trust whichever objective is more volatile at that time,
    encouraging the bandit to favor stable improvements and reduce noisy behavior.

    Smoothed rewards are maintained per-arm using an exponential moving average
    with a tunable smoothing factor `beta`.
    """

    def __init__(self, lambdas, window_size=100, c=0.2, beta=0.2, logger=None):
        """
        Initialize the UCB multi-objective bandit.

        :param lambdas: List of discrete candidate lambda values (arms).
        :param window_size: Window size to compute variance and running averages.
        :param c: UCB exploration factor. Higher = more exploration.
        :param beta: Reward smoothing factor (exponential moving average weight).
        :param logger: Optional logger instance to output reward traces.
        """
        self.lambdas = lambdas
        self.window_size = window_size
        self.c = c
        self.beta = beta

        self.fairness_history = []
        self.rbo_history = []

        self.total_steps = 0
        self.action_counts = np.zeros(len(lambdas))
        self.smoothed_rewards = np.zeros(len(lambdas))

        self.logger = logger

    def select_lambda(self):
        """
        Select the lambda (rec_weight) to use using the UCB formula.

        UCB balances exploration (trying underused arms) and exploitation (choosing high-reward arms).
        If an arm hasn't been selected yet, it's assigned infinite score to force exploration.
        """
        ucb_values = np.zeros(len(self.lambdas))
        for i in range(len(self.lambdas)):
            if self.action_counts[i] == 0:
                ucb_values[i] = float("inf")
            else:
                mean_reward = self.smoothed_rewards[i]
                exploration_bonus = self.c * np.sqrt(
                    np.log(self.total_steps + 1) / self.action_counts[i]
                )
                ucb_values[i] = mean_reward + exploration_bonus

        best_index = np.argmax(ucb_values)
        return self.lambdas[best_index], best_index

    def update(self, selected_index, rl_scores):
        """
        Update the bandit's state using the observed RBO and fairness scores.

        - Computes the harmonic mean between tail and female fairness scores.
        - Tracks rolling windows of RBO and fairness values.
        - Computes alpha dynamically from variance ratios.
        - Combines RBO and fairness using alpha to compute reward.
        - Updates smoothed reward using exponential moving average (EMA).
        - Logs the reward entry if logger is provided.
        """
        rbo_score = rl_scores["rbo"]["score"]
        fairness_tail = rl_scores["fairness"]["tail"]["score"]
        fairness_female = rl_scores["fairness"]["female"]["score"]

        # Harmonic mean of fairness agents to penalize imbalance
        eps = 1e-6
        fairness_harmonic = 2 / (
            1 / (fairness_tail + eps) + 1 / (fairness_female + eps)
        )

        # Track histories for dynamic weighting
        self.rbo_history.append(rbo_score)
        self.fairness_history.append(fairness_harmonic)

        if len(self.rbo_history) > self.window_size:
            self.rbo_history.pop(0)
            self.fairness_history.pop(0)

        # Dynamic alpha favors the more volatile objective
        rbo_var = np.var(self.rbo_history) if len(self.rbo_history) > 1 else 1e-6
        fair_var = (
            np.var(self.fairness_history) if len(self.fairness_history) > 1 else 1e-6
        )
        alpha = rbo_var / (rbo_var + fair_var)

        # Final reward combines accuracy (RBO) and fairness
        rbo_avg = np.mean(self.rbo_history) if self.rbo_history else rbo_score
        reward = alpha * rbo_avg + (1 - alpha) * fairness_harmonic

        # Smoothed reward (EMA)
        previous = self.smoothed_rewards[selected_index]
        smoothed = self.beta * reward + (1 - self.beta) * previous
        self.smoothed_rewards[selected_index] = smoothed

        self.action_counts[selected_index] += 1
        self.total_steps += 1

        # Logging
        if self.logger:
            log_entry = {
                "step": self.total_steps,
                "lambda": self.lambdas[selected_index],
                "reward": reward,
                "running_avg_reward": smoothed,
                "rbo_running_avg": rbo_avg,
                "rl_scores": rl_scores,
            }
            self.logger.info("RL_SCORE_ENTRY: %s", json.dumps(log_entry))

    def step(self, rl_scores):
        """
        Full update cycle:
        - Select lambda using UCB
        - Apply it and observe RL scores
        - Update internal stats and log the outcome
        """
        selected_lambda, selected_index = self.select_lambda()
        self.update(selected_index, rl_scores)
        return selected_lambda
