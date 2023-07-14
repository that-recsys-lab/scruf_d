from abc import ABC, abstractmethod
from scruf.util import PropertyMixin
import jsonlines
from pathlib import Path
from scruf.util import get_path_from_keys, get_value_from_keys, ConfigKeys, InvalidPostProcessorError, \
    UnregisteredPostProcessorError

class PostProcessor(PropertyMixin,ABC):

    def __init__(self):
        super().__init__()
        self.history = None

    @staticmethod
    def read_history(history_file):
        entries = []
        with jsonlines.open(history_file) as reader:
            for obj in reader:
                entries.append(obj)
        return entries

    @staticmethod
    def process_results(result_structs):
        return [(entry['item'], entry['score']) for entry in result_structs]

    def entry_iterate(self, keys):
        for entry in self.history:
            val = get_value_from_keys(keys, entry, default=None)
            yield val

    def load_history(self):
        history_path = get_path_from_keys(ConfigKeys.OUTPUT_PATH_KEYS)
        self.history = self.read_history(history_path)

    @abstractmethod
    def process(self):
        pass


class NullPostProcessor(PostProcessor):
    def process(self):
        pass


class PostProcessorFactory:
        """
        A factory class for creating PostProcessor objects.
        """
        _post_processor = {}

        @classmethod
        def register_post_processor(cls, mechanism_type, mechanism_class):
            if not issubclass(mechanism_class, PostProcessor):
                raise InvalidPostProcessorError(mechanism_class)
            cls. _post_processor[mechanism_type] = mechanism_class

        @classmethod
        def register_post_processors(cls, mechanism_specs):
            for mechanism_type, mechanism_class in mechanism_specs:
                cls.register_post_processor(mechanism_type, mechanism_class)

        @classmethod
        def create_post_processor(cls, mechanism_type):
            mechanism_class = cls._post_processor.get(mechanism_type)
            if mechanism_class is None:
                raise UnregisteredPostProcessorError(mechanism_type)
            return mechanism_class()

# Register the processors created above
processor_specs = [("null", NullPostProcessor)]

PostProcessorFactory.register_post_processors(processor_specs)
