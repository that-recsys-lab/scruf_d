# TODO items


## Mechanisms
* Change choice mechanism so that it matches the formal definition (list-based)
* Change implementation to allow random choice among equal scoring alternatives.

## Unit Tests
* Unit tests for lottery mechanisms

## Util

## Data Handling

## Simulation
* Test and document Jupyter notebook usage

## TORS paper
* Finish implementation of proportional fairness metric
* Implement static allocation mechanism
* Implement fairness only random dictator
* File-based context class
* Experiments
  * Static probability
  * Null choice (no fairness)
  * Random dictator (pick single agent lottery based fairness score)
  * Probabilistic serial mechanism 
  * Product (fairness * compatibility)
  * More complex choice mechanisms?
* Metrics
  * graphs of fairness over time
  * fairness regret
  * accuracy regret
  * overall ndcg
  * overall fairness
* Experimental conditions
  * compatibility distributed across users / agents
  * how hard are the fairness targets to meet
    * ranking of protected items
    * proportion of protected items
  * how quickly does the algorithm respond
* Data generation
  * Inputs
    * item agent distributions
    * user type distributions
    * temporal regimes
  * Outputs
    * recommendation lists (50 items x 1000 users)
    * user compatibilities
    * item feature list
  * Could bias recommendation scores by compatibilities
    * norm(mean + compat)

### Known bugs
* least misery, most compatible should pick randomly when there are ties.
* random seed should be part of configuration file
* 

## Specific implementations

### Fairness metrics
* Proportional fairness
* Minimum exposure metrics

Other stuff from the literature?

### Compatibility metrics
* Nasim's entropy measure

Others?

### Allocation mechanism
* Least misery - DONE 
* Random serial dictator
* Probabilistic serial mechanism

### Choice mechanism
* Fixed delta - DONE RB
* Greedy MMR-type
* FA*IR

Others?

## Data handling

* Export to librec-auto project for evaluation

Eventually SCRUF-specific evaluation. 

# Things to think about

* Should we make the configuration data into its own class.
* Should we get rid of the feature name vs feature id distinction
* Should we simplify ResultList and get rid of the history aspect.
* dynamic item database?

# Completed items

## Agents

* Implement the compatibility metric class, similar to the fairness metric.
  Just the ability to create different classes and maybe some basic baselines: Always compatible, never compatible. Use a factory to make it configurable - DONE
* Add compatibility to the fairness agent implementation -DONE
* Add user_agent_compatibility?
* Move fairness metric execution to AgentCollection class - DONE RB
* Move compatibility metric execution to AgentCollection class - DONE RB

## Mechanisms
* Implement the allocation mechanism class. - DONE
* Implement the choice mechanism class. - DONE RB (Might need to revisit this)

## Unit Tests
* Implement unit tests for compatibility metric. DONE RB
* Implement unit tests for allocation mechanism. DONE RB
* Implement unit tests for choice mechanism. DONE RB

## Data handling
* Implement the history class. Basically an updatable set of tables of the inputs and outputs of each part of the system.
  * Components implemented just need to package it up
* Implement the recommendation agent class. Stores recommendations for all the users and retrieves as needed.
* Implement an item data store so we can look up the features of items as needed. - DONE RB
* Also for users, I guess. (Not sure we need)
* Connect history to mechanisms

## Simulation
* Implement a class to hold the experiment state - DONE RB
* Implement a loader that takes the configuration and creates the experiment state
* Implement the simulation loop that links together all the bits.
* Logging so we can keep track and debug.