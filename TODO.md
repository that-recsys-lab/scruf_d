# TODO items

## Agents

* Implement the compatibility metric class, similar to the fairness metric. Just the ability to create different classes and maybe some basic baselines: Always compatible, never compatible. Use a factory to make it configurable - DONE
* Add compatibility to the fairness agent implementation -DONE
* Add user_agent_compatibility?

## Mechanisms
* Implement the allocation mechanism class. - DONE
* Implement the choice mechanism class. -DONE

## Unit Tests
* Implement unit tests for compatibility metric.
* Implement unit tests for allocation mechanism.
* Implement unit tests for choice mechanism.

## Util
* Update Util 

## Data handling
* Implement the history class. Basically an updatable set of tables of the inputs and outputs of each part of the system.
  * Components implemented just need to package it up
* Implement the recommendation agent class. Stores recommendations for all the users and retrieves as needed. 
* Implement an item data store so we can look up the features of items as needed. Also for users, I guess. 

## Simulation
* Implement a class to hold the experiment state
* Implement a loader that takes the configuration and creates the experiment state
* Implement the simulation loop that links together all the bits.
* Logging so we can keep track and debug.

## Specific implementations

### Fairness metrics
* Proportional fairness
* Minimum exposure metrics

Other stuff from the literature?

### Compatibility metrics
* Nasim's entropy measure

Others?

### Allocation mechanism
* Least misery
* Random serial dictator
* Probabilistic serial mechanism

### Choice mechanism
* Fixed delta
* Greedy MMR-type
* FA*IR

Others?

## Data handling

* Export to librec-auto project for evaluation

Eventually SCRUF-specific evaluation. 