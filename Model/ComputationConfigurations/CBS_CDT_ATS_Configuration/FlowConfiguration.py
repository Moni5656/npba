from Model.ComputationConfigurations.ConfigurationTemplate.DefaultFlowConfiguration import \
    DefaultFlowConfiguration


class FlowConfiguration(DefaultFlowConfiguration):
    def __init__(self, regulation_rate=20.0, l_min=0.001, l_max=0.001, flow_type="A",
                 ac_type="LRQ", **kwargs):
        """
            Constructor of a Flow for [1] defined by:
            :param regulation_rate: regulation rate of every flow in Mbit/s
            :param l_min: minimum packet length in Mbit
            :param l_max: maximum packet length in Mbit
            :param flow_type: CDT / A / B / BE
            :param ac_type: arrival curve type: LRQ / LB

        """
        super().__init__(**kwargs)
        self.regulation_rate = regulation_rate
        self.l_min = l_min
        self.l_max = l_max
        self.type = flow_type
        self.ac_type = ac_type

    def make_parameter_dict(self):
        super_dict = super().make_parameter_dict()

        own_dict = {"regulation rate (Mbit/s)": self.regulation_rate, "minimum packet length (Mbit)": self.l_min,
                    "maximum packet length (Mbit)": self.l_max, "flow type (CDT/A/B/BE)": self.type,
                    "arrival curve type (LRQ/LB)": self.ac_type}
        return super_dict | own_dict

    def update_parameter_dict(self, dictionary):
        new_value = float(dictionary["regulation rate (Mbit/s)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.regulation_rate = new_value

        new_value = float(dictionary["minimum packet length (Mbit)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.l_min = new_value

        new_value = float(dictionary["maximum packet length (Mbit)"])
        if new_value < 0:
            raise ValueError("No negative value allowed")
        self.l_max = new_value

        allowed_types = ["CDT", "A", "B", "BE"]
        new_value = str(dictionary["flow type (CDT/A/B/BE)"])
        if new_value not in allowed_types:
            raise ValueError(f"Unknown flow type: '{new_value}'. Expected: {allowed_types}")
        self.type = new_value
        if self.type == "CDT" or self.type == "BE":
            dictionary["is flow of interest"] = False

        allowed_ac_types = ["LRQ", "LB"]
        new_value = str(dictionary["arrival curve type (LRQ/LB)"])
        if new_value not in allowed_ac_types:
            raise ValueError(f"Unknown ac type: '{new_value}'. Expected: {allowed_ac_types}")
        self.ac_type = new_value

        super().update_parameter_dict(dictionary)

    def to_serializable_dict(self) -> dict:
        super_dict = super().to_serializable_dict()
        own_dict = {"regulation_rate": self.regulation_rate, "l_min": self.l_min, "l_max": self.l_max,
                    "type": self.type, "ac_type": self.ac_type}
        return super_dict | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model, flow):
        super_dict = DefaultFlowConfiguration.to_constructor_dict(json_dict, model, flow)
        own_dict = {"regulation_rate": json_dict["regulation_rate"], "ac_type": json_dict["ac_type"],
                    "flow_type": json_dict["type"], "l_min": json_dict["l_min"], "l_max": json_dict["l_max"]}
        return super_dict | own_dict
