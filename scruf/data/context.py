# Context provides the basis of computing the compatibility between an agent and a recommendation
# opportunity (i.e. a user).
from abc import ABC, abstractmethod
from scruf.util import PropertyMixin, InvalidContextClassError, UnregisteredContextClassError
import csv

class Context(PropertyMixin,ABC):

    @abstractmethod
    def get_context(self, user_id):
        pass

class NullContext(Context):

    def get_context(self, user_id):
        return None
    
class CSVContext(Context):
    _PROPERTIES = ["compatibility_file"]
    
    def get_context(self, user_id):
        comp_file = self.get_property("compatibility_file")
        if not comp_file:
            raise ValueError("compatibility_file property not set")

        with open(comp_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user_id"] == user_id:
                    return row
        return None


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
