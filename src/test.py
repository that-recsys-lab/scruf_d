import numpy as np
import pandas as pd
from data import *

class Test:
    def test1(self):
        total_items = 5
        td = db.get_test_list()
        td2 = td.assign(new_m=lambda x: x.protected_items * 100)

        # td['newM'] = (td['protected_items']/total_items)-((1-td['protected_items'])/total_items)
        print(td2.head)
        
        