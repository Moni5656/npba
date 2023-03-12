from Model.ComputationConfigurations.ConfigurationTemplate.AbstractConfiguration import AbstractConfiguration


class DefaultEdgeConfiguration(AbstractConfiguration):
    def __init__(self, link_speed=100.0, **kwargs):
        """
        :param link_speed: link speed in Mbit/s
        """
        super().__init__(**kwargs)
        self.link_speed = link_speed

    def make_parameter_dict(self):
        super_dict = super().make_parameter_dict()
        own_dict = {"link speed (Mbit/s)": self.link_speed}
        return super_dict | own_dict

    def update_parameter_dict(self, dictionary):
        new_value = float(dictionary["link speed (Mbit/s)"])
        if new_value < 0:
            raise ValueError("No negative speeds allowed")
        self.link_speed = new_value
        return super().update_parameter_dict(dictionary)

    def to_serializable_dict(self) -> dict:
        super_dict = super().to_serializable_dict()
        own_dict = {"link_speed": self.link_speed}
        return super_dict | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model, edge):
        super_dict = AbstractConfiguration.to_constructor_dict(json_dict, model, edge)
        own_dict = {"link_speed": json_dict["link_speed"]}
        return super_dict | own_dict
