import numpy as np
import pandas as pd
import random

class Test2:
    def test2(self):
        df = pd.read_csv('./src/datasets/test.csv')
        # print (df.head)
        total_items = 5
        df2 = df.assign(new_m = lambda x: (x.protected_items/total_items) - ((total_items - x.protected_items)/total_items))
        df3 = df.assign(new_c = np.random.choice([0,1,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9], df.shape[0]))
        
        print(df2.head)
        # print(df3.head)

ts = Test2()
t = ts.test2()
