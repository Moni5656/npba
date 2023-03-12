from Model.ComputationConfigurations.ConfigurationTemplate.DefaultEdgeConfiguration import DefaultEdgeConfiguration


class NancyCBSEdgeConfiguration(DefaultEdgeConfiguration):

    def __init__(self, idle_slope_a: float = 50, send_slope_a: float = -50, idle_slope_b: float = 50,
                 send_slope_b: float = -50, is_plot_in_browser: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.is_plot_in_browser: bool = is_plot_in_browser
        self.idle_slope_a: float = idle_slope_a
        self.send_slope_a: float = send_slope_a
        self.idle_slope_b: float = idle_slope_b
        self.send_slope_b: float = send_slope_b

    def to_serializable_dict(self) -> dict:
        own_dict = {"idle_slope_a": self.idle_slope_a, "send_slope_a": self.send_slope_a,
                    "idle_slope_b": self.idle_slope_b, "send_slope_b": self.send_slope_b}
        return super().to_serializable_dict() | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model, edge):
        super_dict = DefaultEdgeConfiguration.to_constructor_dict(json_dict, model, edge)
        own_dict = {"idle_slope_a": json_dict["idle_slope_a"], "send_slope_a": json_dict["send_slope_a"],
                    "idle_slope_b": json_dict["idle_slope_b"], "send_slope_b": json_dict["send_slope_b"]}
        return super_dict | own_dict

    def make_parameter_dict(self):
        super_dict = super().make_parameter_dict()
        own_dict = {"plot in web browser": self.is_plot_in_browser, "idle slope of class A (Mbit)": self.idle_slope_a,
                    "send slope of class A (Mbit)": self.send_slope_a,
                    "idle slope of class B (Mbit)": self.idle_slope_b,
                    "send slope of class B (Mbit)": self.send_slope_b}
        return super_dict | own_dict

    def update_parameter_dict(self, dictionary):
        new_value = float(dictionary["idle slope of class A (Mbit)"])
        if new_value <= 0:
            raise ValueError("Value greater 0 expected")
        self.idle_slope_a = new_value

        new_value = float(dictionary["send slope of class A (Mbit)"])
        if new_value >= 0:
            raise ValueError("Value less than 0 expected")
        self.send_slope_a = new_value

        new_value = float(dictionary["idle slope of class B (Mbit)"])
        if new_value <= 0:
            raise ValueError("Value greater 0 expected")
        self.idle_slope_b = new_value

        new_value = float(dictionary["send slope of class B (Mbit)"])
        if new_value >= 0:
            raise ValueError("Value less than 0 expected")
        self.send_slope_b = new_value

        true_values = ['true', '1', 't', 'y', 'yes']
        false_values = ['false', '0', 'f', 'n', 'no']
        new_value = str(dictionary["plot in web browser"]).lower()
        if new_value in true_values:
            new_value = True
        elif new_value in false_values:
            new_value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.is_plot_in_browser = new_value

        super().update_parameter_dict(dictionary)

        self.make_curve_previews()

    def make_curve_previews(self):
        """
        Creates a plot of the curves associated to this edge configuration.
        """
        nw_config = self.model.network.configurations[self.group_id]
        if self.is_plot_in_browser or nw_config.plot_on_change_in_browser:
            self.is_plot_in_browser = False
            nw_config.plot_link_curves(self.associated_component)
