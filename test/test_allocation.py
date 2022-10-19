
# import packages

# import scipy.stats as stats
# import seaborn as sns
# import matplotlib.pyplot as plt
 
 
# # generate data
# data =stats.norm(scale=1, loc=0).rvs(1000)
 
# # plotting a histogram
# ax = sns.distplot(data,
#                   bins=50,
#                   kde=True,
#                   color='red',
#                   hist_kws={"linewidth": 15,'alpha':1})
# ax.set(xlabel='Normal Distribution', ylabel='Frequency')
 
# plt.show()

import numpy as np
import pandas as pd
import random

class TestAllocation:
    def allocation(self):
        df = pd.read_csv('test.csv')
        print("hello")

ta = TestAllocation()
ta.allocation()



