import numpy as np
import pandas as pd

class Database:
  """contains all the supplied lists and generated lists of recommendations, fairness attributes"""
  Test_List = '/Users/farastu/pyproj/scruf-d/scruf_d/src/datasets/test.csv'
#   Recommender_List = ''
#   Allocation_History = ''
#   Fairness_Attributes= ''


  def get_recommender_list(self):
        return pd.read_csv(self.Recommender_List)
    
  def get_allocation_history(self):
        return pd.read_csv(self.Allocation_History)

  def get_fairness_attributes(self):
        return pd.read_csv(self.Fairness_Attributes)

  def get_test_list(self):
        return pd.read_csv(self.Test_List)



db = Database()
td = db.get_test_list()
print(td)

    
  