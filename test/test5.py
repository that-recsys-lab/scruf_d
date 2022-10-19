import pandas as pd
import numpy as np

df = pd.read_csv('test/test_m.csv')
# print(df)

def calculate_fpi_sum(df):
    t = 100 #total possible number of protected items for 20 users if per user per agent is 5
    n = 40 # number of users in history
    m = 20 #number of users in the window

    fpi_100 = df['fpi_100'].to_numpy()
    fpi_101 = df['fpi_101'].to_numpy()
    fpi_102 = df['fpi_102'].to_numpy()
    # print(fpi_100)

    sum100 = []
    sum101 = []
    sum102 = []

    for i in range(n-m):
      summ100 = np.sum(fpi_100[i:i+m])
      sum100.append(summ100)
      # print(sum_100)

    for i in range(n-m):
      summ101 = np.sum(fpi_101[i:i+m])
      sum101.append(summ101)
      # print(sum_101)

    for i in range(n-m):
      summ102 = np.sum(fpi_102[i:i+m])
      sum102.append(summ102)
      # print(sum_102)

    df2 = pd.DataFrame()
    df2 = df2.assign(sum_100 = sum100)
    df2 = df2.assign(sum_101 = sum101)
    df2 = df2.assign(sum_102 = sum102)
    # print(df2)

    df2.to_csv ('test/export_pi.csv', index = False, header = True)

    # df = df.assign(m_100 = lambda x: (1+(sum_100/t) - ((t - sum_100)/t)))
    # # df2 = df.assign(m_101 = lambda x: (1+(sum_101/t) - ((t - sum_101)/t)))
    # # df2 = df.assign(m_102 = lambda x: (1+(sum_102/t) - ((t - sum_102)/t)))

def calculate_m():
    df = pd.read_csv('test/export_pi.csv')
    print(df)
    t = 100 #total possible number of protected items for 20 users if per user per agent is 5

    for x in range(100, 103):
        df['m_'+str(x)] = (1+(df['sum_'+str(x)]/t) - ((t - df['sum_'+str(x)])/t))
    print(df)

    df.to_csv ('test/export_m.csv', index = False, header = True)



calculate_fpi_sum(df)
calculate_m()

   









# df = pd.DataFrame({'userId':['u1', 'u2', 'u3', 'u4'],
#                     'm100':[0.5, 0.3, 0.4, 0.2],
#                     'm101':[0.4, 0.4, 0.5, 0.2],
#                     'm102':[0.3, 0.5, 0.3, 0.4],})

# df = pd.DataFrame(np.random.randint(1, 5, size=(30, 3)), columns=list('ABC'))
# df.rename(columns={'A': 'fpi_100', 'B': 'fpi_101', 'C': 'fpi_102'}, inplace=True)
# df = pd.read_csv('test_m.csv')
# print(df)

# def calculate_fairness(df):
#     t = 100 #total possible number of protected items for 20 users if per user per agent is 5
#     n = 30 # number of users in history
#     m = 20 #number of users in the window

#     # cols_as_np = df[df.columns[1:]].to_numpy()
#     # for x in range(100, 103):
#     fpi_100 = df['fpi_100'].to_numpy()
#     fpi_101 = df['fpi_101'].to_numpy()
#     fpi_102 = df['fpi_102'].to_numpy()

    # for x in range(100, 103):
    #     fpi_x = df['fpi_'+str(x)].to_numpy()
    #     for i in range(n-m):
    #         sum_x = np.sum(fpi_x[i:i+m])
    #         print(sum_x)
    #         df2 = df.assign(m_100 = lambda x: (1+(sum_x/t) - ((t - sum_x)/t)))

    # print(df2)



    # for i in range(n-20):
    #     sum100 = np.sum(A[i: i+m])
    #     df2 = df.assign(m_x = lambda x: (1+(sum100/t) - ((t - sum100)/t)))
    # print(df2)
# calculate_fairness(df)
# def test3(df):
    
#     t = 100
    
#     m100 = df['m100'].to_numpy()
#     m101 = df['m101'].to_numpy()
#     m102 = df['m102'].to_numpy()

#     new_m_100 = []
#     new_m_101 = []
#     new_m_102 = []

#     n =  len(m100)

#     for i in range(n - 2):
#         sum100 = sum(m100[i: i+2])
#         sum101 = sum(m100[i: i+2])
#         sum102 = sum(m100[i: i+2])

#         new_m_100.append((sum100/t) - ((t - sum100)/t))
#         new_m_101.append((sum101/t) - ((t - sum101)/t))
#         new_m_102.append((sum102/t) - ((t - sum102)/t))

#         df = df.assign({"new_m_100" : new_m_100}) 
#         df = df.assign(new_m_101)
#         df = df.assign(new_m_102)
#         print(df)  

# test3(df) 

# total = df.iloc[0:2].sum()
# print(total)