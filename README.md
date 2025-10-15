# SCRUF-D

SCRUF-D stands for "Social Choice for Recommendation Under Fairness - Dynamic".

This is an implementation of the SCRUF-D architecture, drawn from
Burke, R., Mattei, N., Grozin, V., Voida, A., & Sonboli, N. (2022, July). Multi-agent Social Choice for Dynamic Fairness-aware Recommendation. In Adjunct Proceedings of the 30th ACM Conference on User Modeling, Adaptation and Personalization (pp. 234-244).

Note: require Python 3.9 or earlier due to functions in the Whalrus package.

## See also

* [Code Overview](doc/code_overview.md)
* [Conceptual Overview (incomplete)](doc/paper-summary.md)

## Configuration

A SCRUF experiment is configured using a TOML file with following section. See example below.

### Location

Information about the working directory for the experiment.

### Data

File names for the recommendation input data and the item features data.

### Parameters

Parameters of the SCRUF experiment: list size, for example.

### Agent

Separate sections for each fairness agent.

### Allocation

Specification for the allocation mechanism

### Choice

Specification for the choice mechanism

### Post

Specification for post-processing

```
[location]
path = "your_path/here"
overwrite = "true"

[data]
rec_filename = "recommendations.txt"
feature_filename = "item_features.txt"

[output]
filename = "history_file.json"
dnc = "true"

[parameters]
list_size = 10
iterations = -1 # -1 means run through all the users
initialize = "skip"
history_window_size = 50

[context]
context_class = "csv_context"

[feature]

[feature.country]
name = "Country"
protected_feature = "country"
protected_values = ["ug", "th", "ke", "ha"]

[feature.sector]
name = "Sector"
protected_feature = "sector"
protected_values = [7, 18, 35]

[feature.loan_size]
name = "Loan Size"
protected_feature = "bucket5"
protected_values = [1]

[agent]

[agent.country]
name = "Country"
metric_class = "proportional_fair"
compatibility_class = "entropy"
preference_function_class = "cascade_preference"

[agent.country.metric]
feature = "Country"
proportion = 0.07

[agent.sector]
name = "Sector"
metric_class = "list_exposure"
compatibility_class = "context_compatibility"
preference_function_class = "cascade_preference"

[agent.sector.metric]
feature = "Sector"

[agent.loan_size]
name = "Loan Size"
metric_class = "list_exposure"
compatibility_class = "risk_aversion"
preference_function_class = "cascade_preference"

[agent.loan_size.metric]
feature = "Loan Size"

[allocation]
allocation_class = "weighted_product_allocation"

[allocation.properties]
fairness_exponent = 1.0
compatibility_exponent = 0.7

[choice]
choice_class = "weighted_scoring"

[choice.properties]
recommender_weight 0.1
```
