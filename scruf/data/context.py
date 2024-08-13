# Context provides the basis of computing the compatibility between an agent and a recommendation
# opportunity (i.e. a user).
from abc import ABC, abstractmethod
from collections import defaultdict
from scruf.util import PropertyMixin, InvalidContextClassError, UnregisteredContextClassError, get_path_from_keys
import csv


class Context(PropertyMixin,ABC):

    def setup(self, input_props, names=None):
        super().setup(input_props, names=names)

    # TODO: This is a little confusing since the context object is a container for other
    # things also called contexts. The name of one of these things needs to change.
    @abstractmethod
    def get_context(self, user_id):
        pass

class NullContext(Context):

    def __init__(self):
        super().__init__()

    def setup(self, config):
        pass

    def get_context(self, user_id):
        return None
    
class CSVContext(Context):
    _PROPERTY_NAMES = ["compatibility_file"]

    def __init__(self):
        super().__init__()
        self.compatibility_dict = defaultdict(dict)

    def setup(self, config, names=None):
        super().setup(config['context']['properties'],
                      names=self.configure_names(CSVContext._PROPERTY_NAMES, names))
        comp_file = get_path_from_keys(['context', 'properties', 'compatibility_file'], config,
                                       check_exists=True)

        with open(comp_file, "r") as f:
            reader = csv.DictReader(f, fieldnames=['user_id', 'agent', 'compatibility'])
            for row in reader:
                user_id = row['user_id']
                agent = row['agent']
                compatibility = float(row['compatibility'])
                self.compatibility_dict[user_id][agent] = compatibility
    
    def get_context(self, user_id):
        return self.compatibility_dict[user_id]


class ContextFactory:
    """
    The ContextFactory associates names with class objects so these can be instantiated
    based on configuration information. A context class must registered in the factory before it can be
    created. Note these are all class methods, so an instance of this object never needs to be created.
    """

    _context_classes = {}

    @classmethod
    def register_context_class(cls, context_type, context_class):
        if not issubclass(context_class, Context):
            raise InvalidContextClassError(context_class)
        cls._context_classes[context_type] = context_class

    @classmethod
    def register_context_classes(cls, context_specs):
        for context_type, context_class in context_specs:
            cls.register_context_class(context_type, context_class)

    @classmethod
    def create_context_class(cls, context_type):
        context_class = cls._context_classes.get(context_type)
        if context_class is None:
            raise UnregisteredContextClassError(context_type)
        return context_class()


# Register the context classes created above
context_specs = [("null_context", NullContext), ("csv_context", CSVContext)]

ContextFactory.register_context_classes(context_specs)
