import uuid

from Model.ComputationConfigurations.ConfigurationTemplate.DefaultEdgeConfiguration import DefaultEdgeConfiguration
from Model.Network import Node
from Model.Subject import Subject


class Edge(Subject):

    def __init__(self, name="", uid=None, is_selected=False, start_node: Node = None, end_node: Node = None,
                 configurations=None):
        super().__init__()
        if configurations is None:
            configurations = {}
        if uid is None:
            uid = uuid.uuid4()

        self.id = uid
        self.name = name
        self.start = start_node
        self.end = end_node
        self.configurations: dict[uuid.UUID, DefaultEdgeConfiguration] = configurations
        self.is_selected = is_selected
        start_node.add_edge_node(end_node, self)
        end_node.add_edge_node(start_node, self)

    def to_dict(self) -> dict:
        """
        Returns a dictionary of the edge attributes.
        :return: dictionary containing edge attributes
        """
        configurations = []
        for configuration in self.configurations.values():
            configurations.append(configuration.to_serializable_dict())
        return {"name": self.name, "id": str(self.id), "start_node": str(self.start.id),
                "end_node": str(self.end.id), "configurations": configurations}

    @staticmethod
    def from_json(json_dict, model) -> 'Edge':
        """
        Creates an edge object based on a JSON dictionary.

        :param json_dict: JSON dictionary
        :param model: network model
        :return: instance of an edge
        """
        start_node = model.network.nodes[uuid.UUID(json_dict["start_node"])]
        end_node = model.network.nodes[uuid.UUID(json_dict["end_node"])]
        edge = Edge(name=json_dict["name"], uid=uuid.UUID(json_dict["id"]), start_node=start_node, end_node=end_node)
        for configuration in json_dict["configurations"]:
            group_id = uuid.UUID(configuration["group_id"])
            network_config = model.network.configurations[group_id]
            edge_config_class = network_config.get_edge_configuration_class()
            edge_config_dict = edge_config_class.to_constructor_dict(configuration, model, edge)
            edge.configurations[group_id] = edge_config_class(**edge_config_dict)
        return edge
