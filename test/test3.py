import numpy as np
import pandas as pd
import random


def test():
        df = pd.read_csv('test.csv')
        #print(df.head)
        temp_df = df['protected_items'].to_numpy()
        print(temp_df)
        for i in range(len(temp_df) -2):
            print(temp_df[i: i+2], "sum is :",sum(temp_df[i: i+2]))

        #print( temp_df = df['protected_items'])
test()
    
