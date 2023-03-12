import uuid

from Model import Subject
from Model.Network import Edge


class Node(Subject):

    def __init__(self, name="", uid=None, is_selected=False, x=0, y=0, configurations=None):
        super().__init__()
        if configurations is None:
            configurations = {}
        if uid is None:
            uid = uuid.uuid4()

        self.id = uid
        self.name = name
        self.is_selected = is_selected
        self.x = int(x)
        self.y = int(y)
        self.edges = {}
        self.configurations = configurations

    def to_dict(self) -> dict:
        """
        Creates a JSON dictionary containing node attributes.

        :return: JSON dictionary containing node attributes
        """
        configurations = []
        for configuration in self.configurations.values():
            if configuration is None:
                configurations.append(None)
            else:
                configurations.append(configuration.to_serializable_dict())
        return {"name": self.name, "id": str(self.id), "x": self.x, "y": self.y, "configurations": configurations}

    @staticmethod
    def from_json(node_dict, model):
        """
        Creates a node based on a JSON dictionary.

        :param node_dict: JSON dictionary
        :param model: network model
        :return: an instance of a node
        """
        node = Node(name=node_dict["name"], uid=uuid.UUID(node_dict["id"]), x=node_dict["x"], y=node_dict["y"])
        for configuration in node_dict["configurations"]:
            group_id = uuid.UUID(configuration["group_id"])
            network_config = model.network.configurations[group_id]
            node_config_class = network_config.get_node_configuration_class()
            node_config_dict = node_config_class.to_constructor_dict(configuration, model, node)
            node.configurations[group_id] = node_config_class(**node_config_dict)
        return node

    def add_edge_node(self, node: 'Node', edge: Edge):
        """
        Adds an edge to a node.

        :param node: node object
        :param edge: edge object
        """
        self.edges[node] = edge

    def set_active(self, activity: bool):
        """
        Sets the activity state of a node.

        :param activity: activity state
        """
        self.is_selected = activity
        self.notify((self, "set_selection"))

    def __lt__(self, other):
        """
        Compares nodes based on their ID.

        :param other: other node object
        :return: whether a node is smaller than another node
        """
        if isinstance(other, self.__class__):
            return self.id.__lt__(other.id)
        return super().__lt__(other)

    def __gt__(self, other):
        """
        Compares two nodes based on their ID.

        :param other: other node object
        :return: whether a node is greater than another node
        """
        if isinstance(other, self.__class__):
            return self.id.__gt__(other.id)
        return super().__gt__(other)
