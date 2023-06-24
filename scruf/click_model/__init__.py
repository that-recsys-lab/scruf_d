# This is the location for click models. Click models are optional models of the user's
# interaction with a list of recommendations. (Maybe interaction model would be a better name.
# If a click model is defined, then we generate an interaction history as well as a recommendation history.
from .click_model import ClickModelFactory, ClickModel, NullClickModel, TopItemModel, UniformRandomModel, \
    GeometricModel
