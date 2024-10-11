# TODO items

## Known bugs
+ strip initial spaces from history strings

## Data Handling

## Unit Tests


## Simulation
* Test and document Jupyter notebook usage

## Experiments

* Allocations
  * Probabilistic serial mechanism 
  * Product (fairness * compatibility) lottery (when we have non-binary compatibility)
  * Product allocation
* Choice
  * More complex choice mechanisms?
* Metrics
  * accuracy regret
  * overall ndcg
  * overall fairness (note different from what the agent's measure which is a function of the window)
* Experimental conditions
  * compatibility distributed across users / agents
  * how hard are the fairness targets to meet
    * ranking of protected items
    * proportion of protected items
    * smaller delta values in the reranker
  * different window sizes
  * two-sided compatibilities
  * different initialization setups
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
    * or generate linked data


## Specific implementations

### Fairness metrics
* Proportional fairness
* Minimum exposure metrics
* Generalized cross-entropy 
* Other stuff from the literature?

### Compatibility metrics
* Nasim's entropy measure (separate preprocess)
* Others?

### Allocation mechanism
* Probabilistic serial mechanism

### Choice mechanism
* Greedy MMR-type
* FA*IR

## Data handling

* Export to librec-auto project for evaluation
* Eventually SCRUF-specific evaluation. 

## Mechanisms

## Util
* Implement the ability to provide default scores for items when balloting

# Things to think about
* Do we need to pass the agent list to compute_choice. Not used anywhere?
* Should we make the configuration data into its own class.
* Should we get rid of the feature name vs feature id distinction
* experiments with dynamic item database?
* How to integrate bandit/reinforcement learning
* Click model for additional history

## Data generation (now its own project)
* Data with non-binary compatibilities
* Data with protected group overlap
* Data with linkage between items, users and compatibilities
  * Maybe an inverse latent variable model?
* Use Kiva data / other data sets


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
* Change implementation to allow random choice among equal scoring alternatives.
* Integrate whalrus (https://francois-durand.github.io/whalrus/)
  * Allow creation of whalrus voting functions at run-time through configuration
  * Convert BallotCollection to appropriate type
  * Convert results to ResultList
  * DONE RB

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

## Allocation
* Least misery - DONE 
* Ra ndom serial dictator

## Choice
* Fixed delta - DONE RB
* Change choice mechanism so that it matches the formal definition (list-based)
  * Replace choice scorer with preference generator
  * Reimplement existing choice scorer with preference-based equivalent
  * Replace choice mechanism definition
    * input: list of preferences, list of weights, list length
  * Redefine do_choice to work with new definition
  * Reimplement rescorer as weighted Borda choice
* Null allocation (effectively the same as null_choice) but handy for experimenting


## Paper is done! Yay!
* Implement static allocation mechanism
* Implement fairness only random dictator
* File-based context class
* Finish implementation of proportional fairness metric


