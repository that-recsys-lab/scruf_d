# Code Overview

## Top-level

### scruf.py

* `Scruf`: The main class for running experiments
  * create using a configuration
  * `setup_experiment`: creates all of the elements of the configuration
  * `run_experiment`: runs the experiment
    * `run_loop`: runs one iteration of the experiment (one user)
  * `cleanup_experiment`
* `ScrufState`: global location for the experiment configuration
  * `config`: configuration data
  * `agents`: collection of fairness agents
  * `history`: history of the results of prior iterations
  * `user_data`: recommendation lists representing user arrivals
  * `item_features`: features associated with the recommended items
  * `context`: context representation (enables computation of compatibility)
  * `allocation_mechanism`
  * `choice_mechanism`

## agent module

### agent.py
* `FairnessAgent`
* `AgentCollection`

### fairness_metric.py
* `FairnessMetric`: abstract class
* `FairnessMetricFactory`
* `AlwaysOneFairnessMetric`: One-value metric for testing purposes
  * name: `always_one`
* `AlwaysZeroFairnessMetric`
  * name: `always_zero`

### compatibility_metric.py
* 


