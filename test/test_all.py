import pandas as pd
import numpy as np

df = pd.read_csv('test/list_1.csv')
df2 = pd.read_csv('test/list_2.csv')
df6 = pd.read_csv('test/list_4.csv')
df5 = pd.DataFrame()
df7 = pd.DataFrame()
my_series_data = ()
tag_100 = 'FF'
tag_101 = 'GHI'
tag_102 = 'C3'
u = 10


#1. Read list_1 & list_2 to assign tags to items
def get_items_tagged(df, df2):
    df3 = df2[['itemTag1', 'itemTag2', 'itemTag3']].copy()
    df4 = pd.concat([df3]*u, ignore_index=True)
    df5 = pd.concat([df, df4], axis=1)
    return df5

def get_fa_scores(df5):
    df5['score_fa1'] = np.where(df5['itemTag1'] == tag_100, 1, 0)
    df5['score_fa2'] = np.where(df5['itemTag2'] == tag_101, 1, 0)
    df5['score_fa3'] = np.where(df5['itemTag3'] == tag_102, 1, 0)
    # df['score_fa_'+str(x)]=np.where(df['itemTag_'+str(x)] == 'tag_'+str(x), 1, 0)
    #drop item tags
    df5 = df5.drop(df5.columns[[3, 4, 5]], axis=1)
    # df5.to_csv ('test/export_scores.csv', index = False, header = True)
    # print(df5)
    return df5

    

def get_pi(df5, df6, df7):
    rating_threshold = 3
    u = 1020

    count_fpi100 = 0
    count_fpi101 = 0
    count_fpi102 = 0
    for ind in df5.index:
        
        if ((df5['itemPredictedRating'].iloc[ind] > rating_threshold)) & ((df5['score_fa1'].iloc[ind] == 1)):
            count_fpi100 += 1
        if ((df5['itemPredictedRating'].iloc[ind] > rating_threshold)) & ((df5['score_fa2'].iloc[ind] == 1)):
            count_fpi101 += 1
        if ((df5['itemPredictedRating'].iloc[ind] > rating_threshold)) & ((df5['score_fa3'].iloc[ind] == 1)):
            count_fpi102 += 1
        if ((df5['itemId'].iloc[ind] == 20)):
            uIDH = df['userId'].iloc[ind] + u
            my_series_data = pd.Series([uIDH, count_fpi100, count_fpi101, count_fpi102], index = ['userIdH', 'fpi_100', 'fpi_101', 'fpi_102'])
            df7 = df7.append(my_series_data, ignore_index=True)
            #reset count_fpixxx
            count_fpi100 = 0
            count_fpi101 = 0
            count_fpi102 = 0

    df6 = df6.append(df7, ignore_index = True)
    # print(df6)
    return df6

def calculate_fpi_sum(df6):
    t = 100 #total possible number of protected items for 20 users if per user per agent is 5
    n = 40 # number of users in history
    m = 20 #number of users in the window

    fpi_100 = df6['fpi_100'].to_numpy()
    fpi_101 = df6['fpi_101'].to_numpy()
    fpi_102 = df6['fpi_102'].to_numpy()

    sum100 = []
    sum101 = []
    sum102 = []

    for i in range(n-m):
      summ100 = np.sum(fpi_100[i:i+m])
      sum100.append(summ100)

    for i in range(n-m):
      summ101 = np.sum(fpi_101[i:i+m])
      sum101.append(summ101)   

    for i in range(n-m):
      summ102 = np.sum(fpi_102[i:i+m])
      sum102.append(summ102)
      
    df8 = pd.DataFrame()
    df8 = df8.assign(sum_100 = sum100)
    df8 = df8.assign(sum_101 = sum101)
    df8 = df8.assign(sum_102 = sum102)
    # df2.to_csv ('test/export_pi.csv', index = False, header = True)
    # print (df8)
    return df8

def calculate_m(df8):
    # df = pd.read_csv('test/export_pi.csv')
    # print(df)
    t = 100 #total possible number of protected items for 20 users if per user per agent is 5

    for x in range(100, 103):
        df8['m_'+str(x)] = (1+(df8['sum_'+str(x)]/t) - ((t - df8['sum_'+str(x)])/t))
    # print(df8)
    return df8
    # df.to_csv ('test/export_m.csv', index = False, header = True)

def calculate_c(df8):
    for x in range (100, 103):
        df8['c_'+str(x)] = np.random.choice([0, 1], size=len(df8), p=[0.7, 0.3])
    # print(df8)
    return df8
    # df.to_csv ('test/export_c.csv', index = False, header = True)

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

def choose_agent():
    dfS, df9 = run_scruf1(df, df2, df5, df6, df7, my_series_data)
    # dfS = pd.read_csv('test/export_scores.csv')
    # print(dfS)
    dfB = calculate_bRating(dfS)
    # print(dfB)
    # print(df9)
    

    #allocation 1
    for x in dfB.index:
        if df9['agentId'].iloc[x%10] == 100: # check userid change
            dfB['itemPredictedRating'].iloc[x] = dfB['bRating_100'].iloc[x]
        elif df9['agentId'].iloc[x%10] == 101:
            dfB['itemPredictedRating'].iloc[x] = dfB['bRating_101'].iloc[x]
        else:
            dfB['itemPredictedRating'].iloc[x] = dfB['bRating_102'].iloc[x]

        if (x%19 == 0): #multiple of 19
            df9 = run_scruf2(dfB, df6, df7, my_series_data)
                
    print(dfB)
    # print(df9)

    return dfB

def calculate_bRating(dfS):
    dfS['bRating_100'] = dfS['itemPredictedRating'] + dfS['score_fa1'] 
    dfS['bRating_101'] = dfS['itemPredictedRating'] + dfS['score_fa2'] 
    dfS['bRating_102'] = dfS['itemPredictedRating'] + dfS['score_fa3'] 
    return dfS

def run_scruf1(df, df2, df5, df6, df7, my_series_data):

    dataFrame1 = get_items_tagged(df, df2)
    dataFrame2 = get_fa_scores(dataFrame1)#from here
    dataFrame3 = get_pi(dataFrame2, df6, df7)
    dataFrame4 = calculate_fpi_sum(dataFrame3)
    dataFrame5 = calculate_m(dataFrame4)
    dataFrame6 = calculate_c(dataFrame5)

    dataFrame7 = allocate_agents_1(dataFrame6)
#     # dataFrame7 = allocate_agents_2(dataFrame6)
#     dataFrame7 = allocate_agents_3(dataFrame6)
    # print(dataFrame7)
    return [dataFrame2, dataFrame7]

def run_scruf2(dfB, df6, df7, my_series_data):

    dataFrame3 = get_pi(dfB, df6, df7)
    dataFrame4 = calculate_fpi_sum(dataFrame3)
    dataFrame5 = calculate_m(dataFrame4)
    dataFrame6 = calculate_c(dataFrame5)

    dataFrame7 = allocate_agents_1(dataFrame6)
#     # dataFrame7 = allocate_agents_2(dataFrame6)
#     dataFrame7 = allocate_agents_3(dataFrame6)
    # print(dataFrame7)
    return dataFrame7

# dataFrame8 = run_scruf(df, df2, df5, df6, df7, my_series_data)

# dataFrame1 = get_items_tagged(df, df2)
# dataFrame2 = get_fa_scores(dataFrame1)
# dataFrame3 = get_pi(dataFrame2, df6, df7)
# dataFrame4 = calculate_fpi_sum(dataFrame3)
# dataFrame5 = calculate_m(dataFrame4)
# dataFrame6 = calculate_c(dataFrame5)

# dataFrame7 = allocate_agents_1(dataFrame6)
# dataFrame7 = allocate_agents_2(dataFrame6)
# dataFrame7 = allocate_agents_3(dataFrame6)

dataFrame8 = choose_agent()
