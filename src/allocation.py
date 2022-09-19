class AllocationMechanism:
    def allocate_1(self,agents: List[Agent],fairness_history: Dict[Agent, List[float]]) -> Dict[Agent, float]: # make subclasses for the different variations of allocations
        d = {a: 5.0 for a in agents}
        for a, fairness in fairness_history.items():
            if a in d:
                d[a] += 1.0 - np.sum(fairness[-1:])
        agent = np.random.choice(agents, size=1, p=[d[a] / sum(d.values()) for a in agents])
        return {agent[0]: 1.0}

    def allocate_2(self,agents: List[Agent],fairness_history: Dict[Agent, List[float]]) -> Dict[Agent, float]: # make subclasses for the different variations of allocations
        d = {a: 5.0 for a in agents}
        for a, fairness in fairness_history.items():
            if a in d:
                d[a] += 1.0 - np.sum(fairness[-1:])
        agent = np.random.choice(agents, size=1, p=[d[a] / sum(d.values()) for a in agents])
        return {agent[0]: 1.0}
    
    def allocate_3(self,agents: List[Agent],fairness_history: Dict[Agent, List[float]]) -> Dict[Agent, float]: # make subclasses for the different variations of allocations
        d = {a: 5.0 for a in agents}
        for a, fairness in fairness_history.items():
            if a in d:
                d[a] += 1.0 - np.sum(fairness[-1:])
        agent = np.random.choice(agents, size=1, p=[d[a] / sum(d.values()) for a in agents])
        return {agent[0]: 1.0}    


#3 types of allocation mechanisms are to be implemented