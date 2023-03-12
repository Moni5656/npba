from Model.ComputationConfigurations.ConfigurationTemplate.DefaultEdgeConfiguration import DefaultEdgeConfiguration


class EdgeConfiguration(DefaultEdgeConfiguration):
    def __init__(self, idle_slope_a=50, send_slope_a=-50, idle_slope_b=50, send_slope_b=-50, t_var_min=0, t_var_max=0,
                 t_proc_min=0, t_proc_max=0, **kwargs):
        """
        Constructor of a Link for [1] defined by:
        :param idle_slope_a: idle slope of class A in Mbit
        :param send_slope_a: send slope of class A in Mbit
        :param idle_slope_b: idle slope of class B in Mbit
        :param send_slope_b: send slope of class B in Mbit
        :param t_var_min: minimal transmission delay in s
        :param t_var_max: maximal transmission delay in s
        :param t_proc_min: minimal switch processing time in s
        :param t_proc_max: maximal switch processing time in s
        """
        super().__init__(**kwargs)
        self.idle_slope_A = float(idle_slope_a)
        self.send_slope_A = float(send_slope_a)
        self.idle_slope_B = float(idle_slope_b)
        self.send_slope_B = float(send_slope_b)
        self.t_var_min = float(t_var_min)
        self.t_var_max = float(t_var_max)
        self.t_proc_min = float(t_proc_min)
        self.t_proc_max = float(t_proc_max)

    def make_parameter_dict(self):
        super_dict = super().make_parameter_dict()
        own_dict = {"idle slope of class A (Mbit)": self.idle_slope_A,
                    "send slope of class A (Mbit)": self.send_slope_A,
                    "idle slope of class B (Mbit)": self.idle_slope_B,
                    "send slope of class B (Mbit)": self.send_slope_B,
                    "minimal var time (s)": self.t_var_min, "maximal var time (s)": self.t_var_max,
                    "minimal switch processing time (s)": self.t_proc_min,
                    "maximal switch processing time (s)": self.t_proc_max}
        return super_dict | own_dict

    def update_parameter_dict(self, dictionary):
        new_value = float(dictionary["idle slope of class A (Mbit)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.idle_slope_A = new_value

        new_value = float(dictionary["send slope of class A (Mbit)"])
        if new_value > 0:
            raise ValueError("No positive value allowed")
        self.send_slope_A = new_value

        new_value = float(dictionary["idle slope of class B (Mbit)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.idle_slope_B = new_value

        new_value = float(dictionary["send slope of class B (Mbit)"])
        if new_value > 0:
            raise ValueError("No positive value allowed")
        self.send_slope_B = new_value

        new_value = float(dictionary["minimal switch processing time (s)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.t_proc_min = new_value

        new_value = float(dictionary["maximal switch processing time (s)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.t_proc_max = new_value

        self.t_var_min = float(dictionary["minimal var time (s)"])
        self.t_var_max = float(dictionary["maximal var time (s)"])

        super().update_parameter_dict(dictionary)

    def to_serializable_dict(self) -> dict:
        super_dict = super().to_serializable_dict()
        own_dict = {"idsl_A": self.idle_slope_A, "sdsl_A": self.send_slope_A, "idsl_B": self.idle_slope_B,
                    "sdsl_B": self.send_slope_B, "t_var_min": self.t_var_min, "t_var_max": self.t_var_max,
                    "t_proc_min": self.t_proc_min, "t_proc_max": self.t_proc_max}
        return super_dict | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model, edge):
        super_dict = DefaultEdgeConfiguration.to_constructor_dict(json_dict, model, edge)
        own_dict = {"idle_slope_a": json_dict["idsl_A"], "send_slope_a": json_dict["sdsl_A"],
                    "idle_slope_b": json_dict["idsl_B"], "send_slope_b": json_dict["sdsl_B"],
                    "t_var_min": json_dict["t_var_min"], "t_var_max": json_dict["t_var_max"],
                    "t_proc_min": json_dict["t_proc_min"], "t_proc_max": json_dict["t_proc_max"]}
        return super_dict | own_dict
