import pandas as pd
import numpy as np

df = pd.read_csv('test/list_3.csv')
# print(df)
df2 = pd.read_csv('test/list_4.csv')
# print(df2)
my_series_data = ()
df3 = pd.DataFrame()

def get_pi(df, df2, df3):
    rating_threshold = 3
    u = 1020

    count_fpi100 = 0
    count_fpi101 = 0
    count_fpi102 = 0
    for ind in df.index:
        
        if ((df['itemPredictedRating'].iloc[ind] > rating_threshold)) & ((df['score_fa1'].iloc[ind] == 1)):
            count_fpi100 += 1
        if ((df['itemPredictedRating'].iloc[ind] > rating_threshold)) & ((df['score_fa2'].iloc[ind] == 1)):
            count_fpi101 += 1
        if ((df['itemPredictedRating'].iloc[ind] > rating_threshold)) & ((df['score_fa3'].iloc[ind] == 1)):
            count_fpi102 += 1
        if ((df['itemId'].iloc[ind] == 20)):
            uIDH = df['userId'].iloc[ind] + u
            my_series_data = pd.Series([uIDH, count_fpi100, count_fpi101, count_fpi102], index = ['userIdH', 'fpi_100', 'fpi_101', 'fpi_102'])
            df3 = df3.append(my_series_data, ignore_index=True)
            #reset count_fpixxx
            count_fpi100 = 0
            count_fpi101 = 0
            count_fpi102 = 0

    df2 = df2.append(df3, ignore_index = True)
    print(df2)


   
        # df2 = df2.concat(series_data, ignore_index = True)
        # df2 = df2.assign(userIdH = i+u, fpi_100 = count_fpi100, fpi_101 = count_fpi101, fpi_102 = count_fpi102)
        
            

get_pi(df, df2, df3)
# print(my_series_data)