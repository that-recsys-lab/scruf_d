from .errors import PropertyMismatchError


class PropertyCollection:
    def __init__(self):
        self.property_names = []
        self.properties = {}

    def get_property_names(self):
        return self.property_names

    def get_properties(self):
        return self.properties

    def get_property(self, property_name):
        return self.properties[property_name]

    def setup(self, input_properties: dict, names):
        """
        Checks the properties provided with those expected by the object
        :param input_properties:
        :return:
        """
        self.property_names = names

        self.properties = {}
        input_property_names = input_properties.keys()

        self.check_properties(self.property_names, input_property_names)

        for key in input_property_names:
            self.properties[key] = input_properties[key]

    def check_properties(self, my_properties, input_properties):
        set_my_properties = set(my_properties)
        set_input_properties = set(input_properties)

        diff_left = set_my_properties - set_input_properties
        diff_right = set_input_properties - set_my_properties

        if len(diff_left) == 0 and len(diff_right) == 0:
            return
        else:
            raise PropertyMismatchError(self, list(diff_left), list(diff_right))
