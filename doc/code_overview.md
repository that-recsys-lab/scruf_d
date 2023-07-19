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
  * `allocation_mechanism`: performs allocation based on agent fairness and compatibility state
  * `choice_mechanism`: performs ranking based on agent and recommender ranking
  * `post_processor`: processes the experiment history

## agent module

### agent.py
Fairness agents
* `FairnessAgent`: abstract class
* `AgentCollection`: set of agents

### compatibility_metric.py
Metrics by which agents measure their interest in recommendation opportunities
* `CompatibilityMetric`: abstract class
* `CompatibilityMetricFactory`: factory class
* `AlwaysOneCompatibilityMetric`: One-value metric for testing purposes
  * name: `always_one`
* `AlwaysZeroCompatibilityMetric`
  * name: `always_zero`

### fairness_metric.py
* `FairnessMetric`: abstract class
* `FairnessMetricFactory`: factory class
* `AlwaysOneFairnessMetric`: One-value metric for testing purposes
  * name: `always_one`
* `AlwaysZeroFairnessMetric`
  * name: `always_zero`

### item_feature_fairness.py
Abstract class for fairness metrics that depend on a single item feature
* `ItemFeatureFairnessMetric`: abstract class
  * required property: `feature`
* `ProportionalItemFM`: proportional fairness (note that experimenter supplies the target proportion)
  * name: `proportional_item`
  * required property: `proportion`

### preference_function.py
Abstract class for functions that agents use to calculate preferences over items as part of the choice mechanism
* `PreferenceFunction`: abstract class
* `PreferenceFunctionFactory`: factory class
* `ZeroPreference`: No preference expressed
  * name: `zero_preference`

### binary_preference.py
* `BinaryPreferenceFunction`: Binary preference based on protected feature
  * name: `binary_preference`
  * require properties: `feature`, `delta` An item with a protected value of `feature` will get a score of `delta`. Otherwise, zero.
* `PerturbedBinaryPreferenceFunction`: Random noise added to binary preference to prevent ties
  * name: `perturbed_binary`

### user_agent_compatibility.py
TODO: These classes aren't very well thought out. Do we have other examples of compatibility metrics?
* `UserAgentCompatibilityMetric`: Abstract class for compatibilities that depend on the context (usually just the user)
* `ContextCompatibilityMetric`: (Better name needed) Reads compatibility from context matrix
  * name: `context_compatibility`

## allocation module

### allocation_mechanism.py
* `RandomAllocationMechanism`
  * name: `random_allocation`
* `ScoredAllocationMechanism`: abstract class for allocation mechanisms that use scores
* `ProductAllocationMechanism`: scores using $(1 - f)c$ where $f$ is fairness and $c$ is compatibility
  * name: `product_allocation`
* `WeightedProductAllocationMechanism`: similar to `ProductAllocationMechanism` but formula is $(1-f)^\alpha c^\beta$
  * name: `weighted_product_allocation`
  * required properties: `fairness_exponent`, `compatibility_exponent`
* `LeastFairAllocationMechanism`
  * name: `least_fair`
* `MostCompatibleAllocationMechanism`
  * name: `most_compatible`

### lottery_allocation.py
* `ProductAllocationLottery`: Very similar to `ProductAllocationMechanism` but uses the scoring as a probability distribution and draws a single agent from it.
  * name: `product_lottery`
* `WeightedProductAllocationLottery`: Very similar to `WeightedProductAllocationMechanism` but uses the scoring as a probability distribution and draws a single agent from it.
  * name: `weighted_product_lottery`
  * required properties: `fairness_exponent`, `compatibility_exponent`
* `FairnessAllocationLottery`: Similar to `LeastFairAllocationMechanism` but uses fairness scores to distribute probability and then draws a single agent. 
  * name: `fairness_lottery`
* `StaticAllocationLottery`
  * name: `static_lottery`
  * required properties: `weights` This a list of `[agent, weight]` pairs from which the lottery is formed.
If the total is less than one, then the residual probability is the probability that no agent will be assigned.


## choice module

### choice_mechanism.py
* `ChoiceMechanism`: abstract class for choice mechanisms
* `ChoiceMechanismFactory`: factory class for choice mechanisms
* `NullChoiceMechanism`: Recommendations pass through unmodified.
  * name: `null_choice`

### whalrus_wrapper_mechanism.py
* `WhalrusWrapperMechanism`: Abstract wrapper class for choice mechanisms implemented in Whalrus.
  * required properties: `whalrus_rule`, `recommender_weight`, `tie_breaker`, `ignore_weights`
* `WhalrusWrapperScoring`: For whalrus rules that use scoring (e.g. Borda)
  * name: `whalrus_scoring`
* `WhalrusWrapperOrdinal`: For whalrus rules that don't use scoring, the order-based ones (e.g. Condorcet)
  * name: `whalrus_ordinal`

### wscoring_choice_mechanism.py
* `WScoringChoiceMechanism`: Linearly combines scores to compute output preferences.
  * name: `weighted_scoring`
  * required properties: `recommender_weight`: The other scores come from the allocation phase so only the recommender weight
needs to be specified here.

## data
### context.py
### item_feature_data.py
### training_data.py
### user_arrival_data.py

## history
### history.py
### results_history.py

## post
### default_post_processor.py
### post_processor.py

## util
### ballot_collection.py
### config_util.py
### errors.py
### history_collection.py
### property_collection.py
### result_list.py
### util.py