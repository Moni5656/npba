from Model.ComputationConfigurations.ConfigurationTemplate.DefaultFlowConfiguration import DefaultFlowConfiguration


class RTCToolboxCBSFlowConfiguration(DefaultFlowConfiguration):

    def __init__(self, avb_class: str = "A", is_periodic: bool = True, is_worst_case: bool = False,
                 max_frame_size: int = 64, class_measurement_interval: float = 0.01,
                 max_interval_frame: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.avb_class: str = avb_class
        self.is_periodic: bool = is_periodic
        self.is_worst_case: bool = is_worst_case
        self.max_frame_size: int = max_frame_size
        self.class_measurement_interval: float = class_measurement_interval
        self.max_interval_frame: int = max_interval_frame

    def to_serializable_dict(self) -> dict:
        own_dict = {"avb_class": self.avb_class, "is_periodic": self.is_periodic, "is_worst_case": self.is_worst_case,
                    "max_frame_size": self.max_frame_size,
                    "class_measurement_interval": self.class_measurement_interval,
                    "max_interval_frame": self.max_interval_frame}
        return super().to_serializable_dict() | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model, flow):
        super_dict = DefaultFlowConfiguration.to_constructor_dict(json_dict, model, flow)
        own_dict = {"avb_class": json_dict["avb_class"], "is_periodic": json_dict["is_periodic"],
                    "is_worst_case": json_dict["is_worst_case"], "max_frame_size": json_dict["max_frame_size"],
                    "class_measurement_interval": json_dict["class_measurement_interval"],
                    "max_interval_frame": json_dict["max_interval_frame"]}
        return super_dict | own_dict

    def make_parameter_dict(self):
        own_dict = {"AVB class (A/B/NSR)": self.avb_class,
                    "is periodic": self.is_periodic,
                    "is worst case": self.is_worst_case, "max. frame size (Byte)": self.max_frame_size,
                    "class measurement interval (s)": self.class_measurement_interval,
                    "max. frames per interval": self.max_interval_frame}
        return super().make_parameter_dict() | own_dict

    def update_parameter_dict(self, dictionary):
        allowed_types = ["A", "B", "NSR"]
        new_value = str(dictionary["AVB class (A/B/NSR)"]).upper()
        if new_value in allowed_types:
            self.avb_class = new_value
        else:
            raise ValueError(f"Unknown AVB class: {new_value}")

        if self.avb_class == "NSR":
            dictionary["is flow of interest"] = False

        true_values = ['true', '1', 't', 'y', 'yes']
        false_values = ['false', '0', 'f', 'n', 'no']
        new_value = str(dictionary["is periodic"]).lower()
        if new_value in true_values:
            new_value = True
        elif new_value in false_values:
            new_value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.is_periodic = new_value

        new_value = str(dictionary["is worst case"]).lower()
        if new_value in true_values:
            new_value = True
        elif new_value in false_values:
            new_value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.is_worst_case = new_value

        new_value = int(dictionary["max. frame size (Byte)"])
        if new_value < 0:
            raise ValueError("Negative Value")
        self.max_frame_size = new_value

        new_value = dictionary["class measurement interval (s)"]
        if new_value < 0:
            raise ValueError("Negative Value")
        self.class_measurement_interval = new_value

        new_value = int(dictionary["max. frames per interval"])
        if new_value < 0:
            raise ValueError("Negative Value")
        self.max_interval_frame = new_value

        super().update_parameter_dict(dictionary)
