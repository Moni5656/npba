import uuid
from enum import IntEnum

from Model import ModelFacade, Subject


class Flow(Subject):
    COLORS = ["#3070B3", "#8F81EA", "#B55CA5", "#F7811E", "#FED702", "#D95117", "#9FBA36", "#6A757E", "#9ABCE4",
              "#C9C2F5", "#D6A4CE", "#FAD080", "#FEEE9A", "#F3B295", "#C7D97D", "#DDE2E6"]
    color_index = 0

    def __init__(self, name="", uid=None, is_selected=False, path=None, color=None, highlight_color=None,
                 configurations=None):
        super().__init__()
        self.name = name
        if configurations is None:
            configurations = {}
        if uid is None:
            uid = uuid.uuid4()
        if path is None:
            path = []

        self.id = uid
        self.is_selected = is_selected
        self.path = path
        self.configurations = configurations

        self.color = color
        self.highlight_color = highlight_color
        self.initialize_flow_color()

    def initialize_flow_color(self):
        """
        Initializes the color and highlight color of a flow in the order of the color list.
        """
        if self.color is None:
            self.color = Flow.COLORS[Flow.color_index % len(Flow.COLORS)]
            Flow.color_index += 1
        if self.highlight_color is None:
            self.highlight_color = self.color

    def to_dict(self) -> dict:
        """
        Creates a dictionary of the flow attributes.

        :return: dictionary containing flow attributes
        """
        configurations = []
        for configuration in self.configurations.values():
            configurations.append(configuration.to_serializable_dict())
        return {"name": self.name, "id": str(self.id), "path": [str(node.id) for node in self.path],
                "color": self.color, "highlight_color": self.highlight_color, "configurations": configurations}

    @staticmethod
    def from_json(json_dict: dict, model: ModelFacade) -> 'Flow':
        """
        Creates a flow object based on a JSON dictionary.

        :param json_dict: JSON dictionary
        :param model: network model
        :return: an instance of a flow
        """
        path = []
        for node_id in json_dict["path"]:
            path.append(model.network.nodes[uuid.UUID(node_id)])
        flow = Flow(name=json_dict["name"], uid=uuid.UUID(json_dict["id"]), path=path, color=json_dict["color"],
                    highlight_color=json_dict["highlight_color"])
        for configuration in json_dict["configurations"]:
            group_id = uuid.UUID(configuration["group_id"])
            network_config = model.network.configurations[group_id]
            flow_config_class = network_config.get_flow_configuration_class()
            flow_config_dict = flow_config_class.to_constructor_dict(configuration, model, flow)
            flow.configurations[group_id] = flow_config_class(**flow_config_dict)
        return flow
