# SCRUF-D

SCRUF-D stands for "Social Choice for Recommendation Under Fairness - Dynamic".

This is an implementation of the SCRUF-D architecture, drawn from
Burke, R., Mattei, N., Grozin, V., Voida, A., & Sonboli, N. (2022, July). Multi-agent Social Choice for Dynamic Fairness-aware Recommendation. In Adjunct Proceedings of the 30th ACM Conference on User Modeling, Adaptation and Personalization (pp. 234-244).

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

```
[location]
path = "my/experiment/here"
overwrite = "true"

[data]
rec_filename = "data/recommendations.txt"
feature_filename = "data/item_features.txt"

[output]
path = "results"

[parameters]
list_size = 10
iterations = -1 # -1 means run through all the users
initialize = "skip"

[agent]

[agent.country]
name = "Country"
metric_class = "proportional_fair"
compatibility = "entropy"

[agent.country.metric]
protected_feature = "country"
protected_values = ["ug", "th", "ke", "ha"]

[agent.sector]
name = "Sector"
metric_class = "list_exposure"
compatibility = "entropy"

[agent.sector.metric]
protected_feature = "sector"
protected_values = [7, 18, 35]

[agent.loan_size]
name = "Loan Size"
metric_class = "list_exposure"
compatibility = "risk_aversion"

[agent.loan_size.metric]
protected_feature = "bucket5"
protected_values = [1]

[allocation]
algorithm = "lottery_single"
history_length = 10

[choice]
algorithm = "fixed_utility"
delta = 0.5
alpha = 0.2
```
