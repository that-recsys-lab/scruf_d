from fairness_agents import *

class baseExeriment:
    fa = SimpleFairnessAgent()
    a = AllocationMechanism()
    c = ChoiceMechanism()

    def experiment_one():
        fa.func1(df)
        fa.func2()
        a.func11()
        c.func0()


#Define base experiment class
#Base experiment class will have the following methods:
#1. Boosted Ratings: 
