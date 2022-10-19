import numpy as np
import pandas as pd
import random

class Test2:
    def test2(self):
        #df = pd.DataFrame(pd.read_excel("test_protect.xlsx"))
        df = pd.read_csv('test_protect.csv')
        # print (df.head)
        total_items = 5
        df2 = df.assign(new_m = lambda x: (x.protected_items/total_items) - ((total_items - x.protected_items)/total_items))
        df.assign()
        #df3 = df.assign(new_c = np.random.choice([0,1,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9], df.shape[0]))
        
        print(df2.head)
        # print(df3.head)
    def test3(self):
        t= 100
        #df = pd.DataFrame(pd.read_excel("test_protect.xlsx"))
        df = pd.read_csv('test_protect.csv')
        c100_pi = df['100_pi'].to_numpy()
        c101_pi = df['101_pi'].to_numpy()
        c102_pi = df['102_pi'].to_numpy()

        new_m_100 = []
        new_m_101 = []
        new_m_102 = []

        n =  len(c100_pi)

        for i in range(n - 20):
            sum100 = sum(c100_pi[i: i+20])
            sum101 = sum(c101_pi[i: i+20])
            sum102 = sum(c102_pi[i: i+20])

            new_m_100.append((sum100/t) - ((t - sum100)/t))
            new_m_101.append((sum101/t) - ((t - sum101)/t))
            new_m_102.append((sum102/t) - ((t - sum102)/t))

        df = df.assign({"new_m_100" : new_m_100})
        #df = df.assign(new_m_101)
        #df = df.assign(new_m_102)
        print(df)   


    def  generate_rnadom_number(self):
        print(random.uniform(0, 1))
        

ts = Test2()
#ts = ts.test2()
ts.test3()
# ts.generate_rnadom_number()
