from Model.ComputationConfigurations.ConfigurationTemplate.AbstractConfiguration import AbstractConfiguration


class DefaultFlowConfiguration(AbstractConfiguration):
    def __init__(self, is_flow_of_interest=True, **kwargs):
        super().__init__(**kwargs)
        self.is_flow_of_interest = is_flow_of_interest

    def make_parameter_dict(self):
        super_dict = super().make_parameter_dict()
        own_dict = {"is flow of interest": self.is_flow_of_interest}
        return super_dict | own_dict

    def update_parameter_dict(self, dictionary):
        true_values = ['true', '1', 't', 'y', 'yes']
        false_values = ['false', '0', 'f', 'n', 'no']
        new_value = str(dictionary["is flow of interest"]).lower()
        if new_value in true_values:
            new_value = True
        elif new_value in false_values:
            new_value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")

        if new_value != self.is_flow_of_interest:
            if new_value:
                self.model.add_flow_of_interest(self.group_id, self.associated_component)
            else:
                self.model.remove_flow_of_interest(self.group_id, self.associated_component)

        return super().update_parameter_dict(dictionary)

    def to_serializable_dict(self) -> dict:
        super_dict = super().to_serializable_dict()
        own_dict = {"is_flow_of_interest": self.is_flow_of_interest}
        return super_dict | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model, flow):
        super_dict = AbstractConfiguration.to_constructor_dict(json_dict, model, flow)
        return super_dict | {"is_flow_of_interest": json_dict["is_flow_of_interest"]}
