from abc import ABC, abstractmethod
from scruf.util import PropertyMixin, InvalidClickModelError, UnregisteredClickModelError, \
    ResultList
import scruf
import random


# RB: It might be more efficient to initialize the click model with a distribution and then
# select using the distribution, rather than scan the list every time?
# This implementation returns a list but it is always one item or empty.
class ClickModel(PropertyMixin,ABC):
    @abstractmethod
    def generate_clicks(self, results: ResultList):
        pass

    def do_clicks(self, output: ResultList, user_recs: ResultList):
        # user recs is here in case we want to have personalized click modeling in the future
        clicks = self.generate_clicks(output)
        scruf.Scruf.state.history.click_history.add_item(clicks)
        return clicks


# The NullClickModel just passes along the whole list
class NullClickModel(ClickModel):
    def generate_clicks(self, results):
        return results


class TopItemModel(ClickModel):
    def generate_clicks(self, results):
        clicks = ResultList()
        top_result = results.get_results()[0]
        clicks.add_result(top_result.user, top_result.item, top_result.score)
        return clicks


class UniformRandomModel(ClickModel):
    _PROPERTY_NAMES = ['reserve_probability']

    def generate_clicks(self, results):
        rand = scruf.Scruf.state.rand
        clicks = ResultList()

        reserve_prob = float(self.get_property('reserve_probability'))
        no_results = rand.choices([0,1], weights=[1 - reserve_prob, reserve_prob], k=1)
        if no_results[0] == 1:
            return clicks

        results_count = len(results.get_results())
        to_click = rand.randint(0, results_count)
        clicked_result = results.get_results()[to_click]
        clicks.add_result(clicked_result.user, clicked_result.item, clicked_result.score)
        return clicks


# The probability at each point is the same but we only proceed in case of failure.
class GeometricModel(ClickModel):
    _PROPERTY_NAMES = ['reserve_probability', 'click_probability']

    def generate_clicks(self, results):
        rand = scruf.Scruf.state.rand
        clicks = ResultList()

        reserve_prob = float(self.get_property('reserve_probability'))
        no_results = rand.choices([0,1], weights=[1 - reserve_prob, reserve_prob], k=1)
        if no_results[0] == 1:
            return clicks

        click_prob = float(self.get_property('click_probability'))
        result_list = results.get_results()
        for entry in result_list[0:-1]:
            pick_this = rand.choices([0,1], weights=[1 - click_prob, click_prob], k=1)
            if pick_this[0] == 1:
                clicks.add_result(entry.user, entry.item, entry.score)
                return clicks

        clicks.add_result(result_list[-1].user, result_list[-1].item, result_list[-1].score)
        return clicks



class ClickModelFactory:
    """
    A factory class for creating ClickModel objects.
    """

    _click_model = {}

    @classmethod
    def register_click_model(cls, model_type, model_class):
        if not issubclass(model_class, ClickModel):
            raise InvalidClickModelError(model_class)
        cls._click_model[model_type] = model_class

    @classmethod
    def register_click_models(cls, model_specs):
        for model_type, model_class in model_specs:
            cls.register_click_model(model_type, model_class)

    @classmethod
    def create_click_model(cls, model_type):
        model_class = cls._click_model.get(model_type)
        if model_class is None:
            raise UnregisteredClickModelError(model_type)
        return model_class()


# Register the models created above
model_specs = [("null_click", NullClickModel),
                   ("top_item_click", TopItemModel),
                   ("uniform_random_click", UniformRandomModel),
                   ("geometric_click", GeometricModel)]

ClickModelFactory.register_click_models(model_specs)
