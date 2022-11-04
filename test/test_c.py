import pandas as pd
import numpy as np
import random

df = pd.read_csv('test/export_m.csv')

def calculate_c(df):
    for x in range (100, 103):
        df['c_'+str(x)] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])
    return df
# df.to_csv ('test/export_c.csv', index = False, header = True)
calculate_c(df)
# df.to_csv ('test/export_c.csv', index = False, header = True)
print(df)
