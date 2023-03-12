import json
import uuid
from typing import Type, Union, Optional

from Model import Subject, ModelFacade
from Model.ComputationConfigurations.ConfigurationTemplate import AbstractNetworkConfiguration
from Model.Network.Edge import Edge
from Model.Network.Flow import Flow
from Model.Network.Node import Node


class Network(Subject):

    def __init__(self, network_id=None, is_selected=True, nodes=None, edges=None, flows=None, configurations=None,
                 name="Network", model=None, node_counter=0, edge_counter=0, flow_counter=0, config_counter=0,
                 information_text=""):
        super().__init__()
        if configurations is None:
            configurations = {}
        if edges is None:
            edges = {}
        if flows is None:
            flows = {}
        if nodes is None:
            nodes = {}
        if network_id is None:
            self.id = uuid.uuid4()
        else:
            self.id = network_id
        self.is_selected = is_selected
        self.nodes: dict[uuid.UUID, Node] = nodes
        self.node_counter = node_counter
        self.edges: dict[uuid.UUID, Edge] = edges
        self.edge_counter = edge_counter
        self.flows: dict[uuid.UUID, Flow] = flows
        self.flow_counter = flow_counter
        self.configurations = configurations
        self.configs_counter = config_counter
        self.name = name
        self.information_text = information_text
        self.selected_components = []
        self.model = model

    def add_node(self, node: Node):
        """
        Adds a node to the network.

        :param node: node object
        """
        if node.is_selected:
            self.add_selected_component(node)
        self.nodes[node.id] = node
        for config in self.configurations.values():
            node_config = config.get_node_configuration_class()(
                group_id=config.group_id, model=self.model, associated_component=node)
            node.configurations[config.group_id] = node_config

    def delete_node(self, node: Node):
        """
        Deletes a node from the network.

        :param node: node object
        """
        for flow in list(self.flows.values()):
            if node in flow.path:
                self.delete_flow(flow)

        for edge in list(node.edges.values()):
            self.delete_edge(edge)

        if node in self.selected_components:
            self.selected_components.remove(node)
        del self.nodes[node.id]
        self.notify((node, "delete_node"))

    def add_edge(self, edge: Edge):
        """
        Adds an edge to the network.

        :param edge: edge object
        """
        if edge.is_selected:
            self.add_selected_component(edge)
        self.edges[edge.id] = edge
        for config in self.configurations.values():
            edge_config = config.get_edge_configuration_class()(group_id=config.group_id,
                                                                model=self.model, associated_component=edge)
            edge.configurations[config.group_id] = edge_config

    def delete_edge(self, edge: Edge):
        """
        Deletes an edge from the network.

        :param edge: edge object
        """
        for flow in list(self.flows.values()):
            if self.is_edge_in_path(edge, flow.path):
                self.delete_flow(flow)

        del edge.start.edges[edge.end]
        del edge.end.edges[edge.start]
        if edge in self.selected_components:
            self.selected_components.remove(edge)
        del self.edges[edge.id]

        self.notify((edge, "delete_edge"))
        edge.start.notify((edge, "delete_edge"))
        edge.end.notify((edge, "delete_edge"))

    def add_flow(self, flow: Flow):
        """
        Adds a flow to the network.

        :param flow: flow object
        """
        if flow.is_selected:
            self.add_selected_component(flow)
        self.flows[flow.id] = flow
        for config in self.configurations.values():
            config.flow_ids_of_interest.append(flow.id)
            config.notify((config, "set_parameter"))
            flow_config = config.get_flow_configuration_class()(group_id=config.group_id,
                                                                model=self.model, associated_component=flow)
            flow.configurations[config.group_id] = flow_config

    def delete_flow(self, flow: Flow):
        """
        Deletes a flow from the network.

        :param flow: flow object
        """
        for config in self.configurations.values():
            if flow.id in config.flow_ids_of_interest:
                config.flow_ids_of_interest.remove(flow.id)
                config.notify((config, "set_parameter"))
        self.notify((flow, "delete_flow"))
        if flow in self.selected_components:
            self.selected_components.remove(flow)
        del self.flows[flow.id]

    def add_selected_component(self, component: Union[Node, Edge, Flow]):
        """
        Adds a component to the list of selected components.

        :param component: component object
        """
        self.selected_components.append(component)

    @staticmethod
    def is_edge_in_path(edge: Edge, path: list[Node]):
        """
        Checks whether an edge is contained in a flow path.

        :param edge: edge object
        :param path: path
        :return: whether an edge is contained in a path
        """
        if edge.start in path and edge.end in path:
            i = path.index(edge.start)
            if i > 0 and path[i - 1] == edge.end:
                return True
            elif i < len(path) - 1 and path[i + 1] == edge.end:
                return True
        return False

    def add_config(self, config: AbstractNetworkConfiguration):
        """
        Adds a computation configuration to the network.

        :param config: configuration object
        """
        self.configurations[config.id] = config

    def update_name(self, value: str):
        """
        Updates the network name.

        :param value: new name
        """
        self.name = value
        self.notify((self, "name"))

    def to_json(self) -> str:
        """
        Creates a dictionary of the network attributes.

        :return: a JSON dictionary containing network attributes
        """
        configurations = []
        for configuration in self.configurations.values():
            configurations.append(configuration.to_serializable_dict())
        json_dict = {"name": self.name, "id": str(self.id), "information": self.information_text,
                     "node_counter": self.node_counter, "edge_counter": self.edge_counter,
                     "flow_counter": self.flow_counter, "configuration_counter": self.configs_counter, "nodes": [],
                     "edges": [], "flows": [], "configurations": configurations}
        for node_id in self.nodes:
            node = self.nodes[node_id]
            json_dict["nodes"].append(node.to_dict())
        for edge_id in self.edges:
            edge = self.edges[edge_id]
            json_dict["edges"].append(edge.to_dict())
        for flow_id in self.flows:
            flow = self.flows[flow_id]
            json_dict["flows"].append(flow.to_dict())
        return json.dumps(json_dict, indent=2)

    @staticmethod
    def from_json(json_dict, model: ModelFacade):
        """
        Creates a network object based on a JSON dictionary.

        :param json_dict: JSON dictionary
        :param model: network model
        :return: instance of a network
        """
        network = Network(network_id=uuid.UUID(json_dict["id"]), name=json_dict["name"], model=model,
                          information_text=json_dict["information"], node_counter=json_dict["node_counter"],
                          edge_counter=json_dict["edge_counter"], flow_counter=json_dict["flow_counter"],
                          config_counter=json_dict["configuration_counter"])
        model.network = network
        for configuration in json_dict["configurations"]:
            configuration_class_str = configuration["_configuration_class"]
            network_configuration_class: Optional[Type['AbstractNetworkConfiguration']] = \
                Network._get_configuration_from_string(configuration_class_str)
            if network_configuration_class is None:
                raise FileNotFoundError(
                    f"Configuration type \"{configuration_class_str}\" has no matching python implementation")

            constructor_dict = network_configuration_class.to_constructor_dict(json_dict=configuration,
                                                                               model=model, network=network)
            network_configuration = network_configuration_class(**constructor_dict)
            network.configurations[network_configuration.group_id] = network_configuration

        for node_dict in json_dict["nodes"]:
            node = Node.from_json(node_dict, model)
            network.nodes[node.id] = node

        for edge_dict in json_dict["edges"]:
            edge = Edge.from_json(edge_dict, model)
            network.edges[edge.id] = edge

        for flow_dict in json_dict["flows"]:
            flow = Flow.from_json(flow_dict, model)
            network.flows[flow.id] = flow

        return network

    @staticmethod
    def _get_configuration_from_string(configuration_class_str):
        """
        Maps a given string to a configuration class.

        :param configuration_class_str: string identifier
        :return: configuration object
        """
        import Model
        for network_configuration in Model.get_available_network_configurations().values():
            if network_configuration.get_configuration_identifier() == configuration_class_str:
                return network_configuration
        return None
