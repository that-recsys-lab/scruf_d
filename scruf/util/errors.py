
class ScrufError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PropertyMismatchError(ScrufError):
    def __init__(self, obj, missing_props=None, extra_props=None):
        self.message = f'Creating {obj.__class__} Missing properties {missing_props}, Unexpected properties {extra_props}'
        super().__init__(self.message)


class InvalidFairnessMetric(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create fairness metric: Class {name} is not a subclass of FairnessMetric.'
        super().__init__(self.message)

class UnregisteredFairnessMetric(ScrufError):
    def __init__(self, name):
        self.message = f'Cannot create fairness metric: Class {name} is not registered and may not exist.'
        super().__init__(self.message)
