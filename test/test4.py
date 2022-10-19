import pandas as pd
import numpy as np

df = pd.DataFrame({'userId':['u1', 'u2', 'u3', 'u4'],
                    'm100':[0.5, 0.3, 0.4, 0.2],
                    'm101':[0.4, 0.4, 0.5, 0.2],
                    'm102':[0.3, 0.5, 0.3, 0.4],
                    'c100':[0, 0, 1, 1],
                    'c101':[1, 0, 0, 0],
                    'c102':[0, 1, 0, 1]})
df2 = pd.read_csv('test_protect.csv')
# def allocate_agents_1(df):
#     df['min'] = df[['m100','m101','m102']].idxmin(axis=1)

#     df['Ba1_100'] = np.where(df['min'] == 'm100', 1, 0)
#     df['Ba1_101'] = np.where(df['min'] == 'm101', 1, 0)
#     df['Ba1_102'] = np.where(df['min'] == 'm102', 1, 0)
#     print(df)

def allocate_agents_11(df):
    df['min'] = df[['m100','m101','m102']].idxmin(axis=1)
    for x in range(100, 103):
        df['Ba1_'+str(x)]=np.where(df['min'] == 'm'+str(x), 1, 0)
    print(df)       

# def allocate_1(self,agents: List[Agent],fairness_history: Dict[Agent, List[float]]) -> Dict[Agent, float]: # make subclasses for the different variations of allocations
#     d = {a: 5.0 for a in agents}
#     for a, fairness in fairness_history.items():
#         if a in d:
#             d[a] += 1.0 - np.sum(fairness[-1:])
#     agent = np.random.choice(agents, size=1, p=[d[a] / sum(d.values()) for a in agents])
#     return {agent[0]: 1.0}

# def allocate_agents_2(df):
#     df['max'] = df[['c100','c101','c102']].idxmax(axis=1)
#     df['Ba2_100'] = np.where(df['max'] == 'c100', 1, 0)
#     df['Ba2_101'] = np.where(df['max'] == 'c101', 1, 0)
#     df['Ba2_102'] = np.where(df['max'] == 'c102', 1, 0)
#     print(df)

allocate_agents_11(df)
# allocate_agents_2(df)