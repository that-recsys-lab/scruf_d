import pandas as pd
import numpy as np

df = pd.read_csv("test/test_b.csv")
# print(df.head)
tag_100 = 'FF'
tag_101 = 'GHI'
tag_102 = 'C3'

def calculate_boosted_test(df):

    # df['Score_fa_100'] = np.where(df['itemTag_100'] == 'FF', 1, 0)
    # df['Score_fa_101'] = np.where(df['itemTag_101'] == 'GHI', 1, 0)
    # df['Score_fa_102'] = np.where(df['itemTag_102'] == 'C3', 1, 0)

    df['Score_fa_100'] = np.where(df['itemTag_100'] == tag_100, 1, 0)
    df['Score_fa_101'] = np.where(df['itemTag_101'] == tag_101, 1, 0)
    df['Score_fa_102'] = np.where(df['itemTag_102'] == tag_102, 1, 0)

    return df

def calculate_boosted(df):
    for x in range(100, 103):
        # if df['itemTag_'+str(x)] == 'tag_'+str(x):
        #     df['Score_fa_'+str(x)] = 1
        # else:
        #     df['Score_fa_'+str(x)] = 0
        
        df['Score_fa_'+str(x)]=np.where(df['itemTag_'+str(x)] == 'tag_'+str(x), 1, 0)
    return df

def calculate_bRating():
    df['bRating_100'] = df['rating'] + df['Score_fa_100'] 
    df['bRating_101'] = df['rating'] + df['Score_fa_101'] 
    df['bRating_102'] = df['rating'] + df['Score_fa_102'] 


calculate_boosted_test(df)
# calculate_boosted(df)
# calculate_bRating()
print(df)
