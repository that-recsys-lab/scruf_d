class ChoiceMechanism:

  def choice_1():
    def choose(self, allocation: Dict[Agent, float]) -> Agent:
        agents, probas = list(allocation.keys()), np.array(list(allocation.values()))
        probas = probas / np.sum(probas)
        chosen = np.random.choice(agents, size=1, p=probas)[0]
        return chosen

    def apply_agent(self,agent: Agent, predicted_score: Dict[str, float]) -> Dict[str, float]:
        pref = agent.preference()
        scores = {i: predicted_score.get(i, 0.0) + pref.get(i, 0.0) for i in predicted_score}
        return scores


#There is only 1 type of choice mechanism