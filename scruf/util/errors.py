
class ScrufError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PropertyMismatchError(ScrufError):
    def __init__(self, obj, missing_props=None, extra_props=None):
        self.message = f'Creating {obj.__class__} Missing properties {missing_props}, Unexpected properties {extra_props}'
        super().__init__(self.message)


class InvalidFairnessMetricError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create fairness metric: Class {name} is not a subclass of FairnessMetric.'
        super().__init__(self.message)


class UnregisteredFairnessMetricError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create fairness metric: Class {name} is not registered and may not exist.'
        super().__init__(self.message)


class InvalidCompatibilityMetricError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create compatibility metric: Class {name} is not a subclass of CompatibilityMetric.'
        super().__init__(self.message)


class UnregisteredCompatibilityMetricError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create compatibility metric: Class {name} is not registered and may not exist.'
        super().__init__(self.message)


class HistoryEmptyError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot get items from empty history.'
        super().__init__(self.message)


class ConfigFileError(ScrufError):
    def __init__(self, file):
        self.message = f'Error loading configuration file {file}.'
        super().__init__(self.message)


class ConfigKeyMissingError(ScrufError):
    def __init__(self, key):
        self.message = f'Error in configuration file. Expecting key "{key}".'
        super().__init__(self.message)


class ConfigNoAgentsError(ScrufError):
    def __init__(self):
        self.message = f'Error in configuration file. No fairness agents were specified.'
        super().__init__(self.message)


class InvalidAllocationMechanismError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create allocation mechanism: Class {name} is not a subclass of AllocationMechanism.'
        super().__init__(self.message)


class UnregisteredAllocationMechanismError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create allocation mechanism: Class {name} is not registered and may not exist.'
        super().__init__(self.message)


class InvalidChoiceMechanismError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create choice mechanism: Class {name} is not a subclass of ChoiceMechanism.'
        super().__init__(self.message)


class UnregisteredChoiceMechanismError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create choice mechanism: Class {name} is not registered and may not exist.'
        super().__init__(self.message)


class MismatchedWhalrusRuleError(ScrufError):
    def __init__(self, name, wrapper_name):
        self.message = f'Cannot create choice mechanism: Whalrus rule {name} does not match {wrapper_name}.'
        super().__init__(self.message)

class UnknownWhalrusTiebreakError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create choice mechanism: Whalrus tiebreak {name} is unknown.'
        super().__init__(self.message)


class InvalidPreferenceFunctionError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create preference function: Class {name} is not a subclass of PreferenceFunction.'
        super().__init__(self.message)


class UnregisteredPreferenceFunctionError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create preference function: Class {name} is not registered and may not exist.'
        super().__init__(self.message)


class InvalidContextClassError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create context class: Class {name} is not a subclass of Context.'
        super().__init__(self.message)


class UnregisteredContextClassError(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create context class: Class {name} is not registered and may not exist.'
        super().__init__(self.message)


class MissingFeatureDataFilenameError(ScrufError):
    def __init__(self):
        self.message = f'Cannot set up item feature data: Expecting data.feature_filename in configuration file.'
        super().__init__(self.message)


class PathDoesNotExistError(ScrufError):
    def __init__(self, path, keys):
        self.message = f'Expected path {str(path)} from config file {keys} does not exist.'
        super().__init__(self.message)


class ContextNotFoundError(ScrufError):
    def __init__(self, user_id):
        self.message = f'Context has no entry for user {user_id}.'
        super().__init__(self.message)

class UnknownCollapseParameterError(ScrufError):
    def __init__(self, parameter_type, parameter_value):
        self.message = f'Unknown parameter for collapse_score_dict: parameter {parameter_type} value {parameter_value}'
        super().__init__(self.message)