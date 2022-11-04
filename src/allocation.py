class AllocationMechanism:

    def allocate_agents_1(df8):
    df8['min'] = df8[['m_100','m_101','m_102']].idxmin(axis=1) #fix this
    for x in range(100, 103):
        df8['Ba1_'+str(x)]=np.where(df8['min'] == 'm_'+str(x), 1, 0)
    # print(df8)

    # make choice function
    df8['maxA1'] = df8[['Ba1_100','Ba1_101','Ba1_102']].idxmax(axis=1)
    df8['agentId'] = np.where(df8['maxA1'] == 'Ba1_100', 100, np.where(df8['maxA1'] == 'Ba1_101', 101, 102))

    return df8

def allocate_agents_2(df8):
    df8['max'] = df8[['c_100','c_101','c_102']].idxmax(axis=1)
    for x in range(100, 103):
        df8['Ba2_'+str(x)]=np.where(df8['max'] == 'c_'+str(x), 1, 0)
    # print(df8)
    return df8

def allocate_agents_3(df8):
    for x in range(100, 103):
        df8['Ba3_'+str(x)]= (1 - (df8['m_'+str(x)]) * df8['c_'+str(x)])
    # print(df8)
    return df8




















    # def allocate_agents_11(df):
    # df['min'] = df[['m100','m101','m102']].idxmin(axis=1)
    # for x in range(100, 103):
    #     df['Ba1_'+str(x)]=np.where(df['min'] == 'm'+str(x), 1, 0)
    # print(df)
 


#3 types of allocation mechanisms are to be implemented


#save old code
    # def allocate_1(self,agents: List[Agent],fairness_history: Dict[Agent, List[float]]) -> Dict[Agent, float]: # make subclasses for the different variations of allocations
    #     d = {a: 5.0 for a in agents}
    #     for a, fairness in fairness_history.items():
    #         if a in d:
    #             d[a] += 1.0 - np.sum(fairness[-1:])
    #     agent = np.random.choice(agents, size=1, p=[d[a] / sum(d.values()) for a in agents])
    #     return {agent[0]: 1.0}