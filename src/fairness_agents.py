import numpy as np
import pandas as pd
from data import *

class SimpleFairnessAgent:
  """These fairness agents are associated with specific fairness concerns, assesing different aspects of the items, users, and the recommendation list ls."""

  def __init__(self,get_fairness_attributes()):

        df = self.get_fairness_attributes()
        self.name = name
        self._preference_map = preference_map
        self.list_lookup_horizon = list_lookup_horizon
        return df 

  def fairness_metric(self, df) -> Dict[str, float]:
        return self._preference_map # read from csv 

  def compatibility(self, items: List[str], **kwargs) -> float:
        N = min(self.list_lookup_horizon, len(items))
        list_weights = 1 / np.log(2 + np.arange(len(items)))
        gt = np.array([self._preference_map.get(i, 0.0) for i in items])
        return np.sum(gt[:N] * list_weights[:N]) / np.sum(self.norm[:N] * list_weights[:N])
    

#   td = db.get_test_list()
 
#   def test1(self):
#     total_items = 5
#     td = db.get_test_list()
#     td2 = td.drop(["m", "c", "B_a1", "B_a2", "B_a3"], axis = 1, inplace=True)
    # td['newM'] = (td['protected_items']/total_items)-((1-td['protected_items'])/total_items)
   
    # self.fi = df.fairnessAgentsId
#   rc = db.get_recommender_list()
#   fa = db.get_fairness_attributes()
  
  
#   def __init__(self, name, preference_map: Dict[Any, int], list_lookup_horizon):
#         self.name = name
#         self._preference_map = preference_map
#         self.list_lookup_horizon = list_lookup_horizon
#         self.norm = sorted(self._preference_map.values(), reverse=True)
#         if len(self.norm) < list_lookup_horizon:
#             # Pad with zeroes
#             self.norm.extend([0] * (list_lookup_horizon - len(self.norm)))
#         self.norm = np.array(self.norm)

#   def preference(self, **kwargs) -> Dict[str, float]:
#         return self._preference_map # read from csv 

#   def point_fairness(self, items: List[str], **kwargs) -> float:
#         N = min(self.list_lookup_horizon, len(items))
#         list_weights = 1 / np.log(2 + np.arange(len(items)))
#         gt = np.array([self._preference_map.get(i, 0.0) for i in items])
#         return np.sum(gt[:N] * list_weights[:N]) / np.sum(self.norm[:N] * list_weights[:N])
    
#   def mscore(self, **kwargs):
#       total_items = df_ls['item_count'].sum()
#       score = (((df_ls.groupby("protected")["item_count"].sum())/ total_items) - ((df_ls.groupby("unprotected")["item_count"].sum())/ total_items))
#       return score
#   def compatibility(self, ):
    
#       return 1
#   def preference(self, **kwargs):

fa = SimpleFairnessAgent()
t = fa.test1()
t = fa.preferance()