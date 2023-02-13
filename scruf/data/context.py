# Context provides the basis of computing the compatibility between an agent and a recommendation
# opportunity (i.e. a user).
from abc import ABC, abstractmethod
from scruf.util import PropertyMixin, InvalidContextClassError, UnregisteredContextClassError

class Context(PropertyMixin,ABC):

    @abstractmethod
    def get_context(self, user_id):
        pass

class NullContext(Context):

    def get_context(self, user_id):
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
context_specs = [("null_context", NullContext)]

ContextFactory.register_context_classes(context_specs)