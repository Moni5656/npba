from typing import Union, Callable

import customtkinter as ctk

import Model
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractConfiguration import AbstractConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractNetworkConfiguration import \
    AbstractNetworkConfiguration
from Model.Network import *


class GUIController:

    def __init__(self, model_facade: Model.ModelFacade):
        self.model_facade = model_facade

    def update_parameter(self, new_value, parameter, component: Union[Network, Node, Edge, Flow]):
        """
        Updates parameter values in the model.

        :param new_value: new parameter value
        :param parameter: parameter name
        :param component: network component
        """
        if isinstance(component, Network):
            self._update_network_parameter(new_value, parameter)
        elif isinstance(component, Node):
            self._update_node_parameter(new_value, parameter, component)
        elif isinstance(component, Edge):
            self._update_edge_parameter(new_value, parameter, component)
        elif isinstance(component, Flow):
            self._update_flow_parameter(new_value, parameter, component)

    def _update_network_parameter(self, new_value, parameter):
        """
        Updates parameters of the network object.

        :param new_value: new parameter value
        :param parameter: parameter name
        """
        if parameter == "name":
            self.model_facade.update_network_name(new_value)

    def _update_node_parameter(self, new_value, parameter, node: Node):
        """
        Updates parameters of the node object.

        :param new_value: new parameter value
        :param parameter: parameter name
        :param node: node object
        """
        if parameter == "name":
            self.model_facade.update_node_name(node, new_value)
        if parameter == "x":
            self.model_facade.update_node_x_y(node, int(new_value), node.y)
        if parameter == "y":
            self.model_facade.update_node_x_y(node, node.x, int(new_value))

    def _update_edge_parameter(self, new_value, parameter, edge: Edge):
        """
        Updates parameters of the edge object.

        :param new_value: new parameter value
        :param parameter: parameter name
        :param edge: edge object
        """
        if parameter == "name":
            self.model_facade.update_edge_name(edge, new_value)

    def _update_flow_parameter(self, new_value, parameter, flow: Flow):
        """
        Updates parameters of the flow object.

        :param new_value: new parameter value
        :param parameter: parameter name
        :param flow: flow object
        """
        if parameter == "name":
            self.model_facade.update_flow_name(flow, new_value)
        elif parameter == "color":
            self.model_facade.update_flow_color(flow, new_value)
        elif parameter == "highlight color":
            self.model_facade.update_flow_highlight_color(flow, new_value)

    @staticmethod
    def color_entry_border(entry: ctk.CTkEntry, color: str = "red"):
        """
        Reconfigures the color of an entry border.

        :param entry: entry object
        :param color: Tkinter color
        """
        entry.configure(border_color=color)

    @staticmethod
    def color_entry_on_error(entry: ctk.CTkEntry, value_setter: Callable):
        """
        Reconfigures the according model value or sets border color on invalid input values.

        :param entry: entry object
        :param value_setter: function to change the model value
        """
        try:
            value_setter()
        except ValueError:
            GUIController.color_entry_border(entry)

    def add_configuration(self, first_option: str, second_option: str, third_option: str):
        """
        Adds a computation configuration to the network.

        :param first_option: value of the first drop-down menu
        :param second_option: value of the second drop-down menu
        :param third_option: value of the third drop-down menu
        """
        network_configuration = Model.get_network_configuration_from_options(first_option, second_option, third_option)
        self.model_facade.add_configuration(network_configuration_class=network_configuration)

    def delete_configuration(self, configuration: AbstractNetworkConfiguration):
        """
        Removes a computation configuration from the network.

        :param configuration: configuration object
        """
        self.model_facade.delete_configuration(configuration)

    def add_node(self, x, y, name=None, is_selected=True):
        """
        Adds a node to the network.

        :param x: x coordinate
        :param y: y coordinate
        :param name: name of the node
        :param is_selected: current selection state
        """
        self.model_facade.add_node(x, y, name=name, is_selected=is_selected)

    def add_edge(self, start_node: Node, end_node: Node, name=None, is_selected=True):
        """
        Adds an edge to the network.

        :param start_node: the start node
        :param end_node: the end node
        :param name: name of the edge
        :param is_selected: current selection state
        """
        try:
            self.model_facade.add_edge(start_node, end_node, name=name, is_selected=is_selected)
        except Exception as e:
            self.model_facade.notify_error(e)

    def add_flow(self, start_node: Node, second_node: Node, is_selected=True):
        """
        Adds a flow to the network.

        :param start_node: the start node
        :param second_node: the second node
        :param is_selected: current selection state
        """
        self.model_facade.add_flow(path=[start_node, second_node], is_selected=is_selected)

    def delete_component(self, component: Union[Node, Edge, Flow]):
        """
        Deletes a network component.

        :param component: component object
        """
        self.model_facade.delete_component(component)

    def on_component_click(self, component: Union[Node, Edge, Flow]):
        """
        Handles the selection of a component.

        :param component: component object
        """
        self.model_facade.unselect_all_components()
        self.model_facade.select_component(component, True)

    def on_component_shift_click(self, component: Union[Node, Edge, Flow]):
        """
        Handles the selection of components on Shift-Click.

        :param component: component object
        """
        self.model_facade.select_component(component, True)

    def export_network(self, path: str):
        """
        Exports the current network as JSON.

        :param path: path to the export file
        """
        from View.GUI.GUIWrapper import GUIWrapper
        GUIWrapper.save_to_recent(self.model_facade.network.name, path)
        self.model_facade.export_network(path)

    def import_network(self, path: str):
        """
        Imports a network from a given JSON file.

        :param path: path to the JSON file
        """
        from View.GUI.GUIWrapper import GUIWrapper
        GUIWrapper.save_to_recent(self.model_facade.network.name, path)
        self.model_facade.import_network(path)

    def run_computation(self):
        """
        Runs the computation.
        """
        self.model_facade.run_computation()

    def cancel_computation(self, computation: Model.Computation):
        """
        Cancels a running computation.

        :param computation: computation object
        """
        self.model_facade.cancel_computation(computation)

    def update_configuration_parameters(self, configuration: AbstractConfiguration, dictionary: dict):
        """
        Updates parameters of a configuration.

        :param configuration: configuration object
        :param dictionary: parameter dictionary
        """
        self.model_facade.update_configuration_parameters(configuration, dictionary)

    def generate_random_network(self, seed=None, min_num_nodes=100, max_num_nodes=150, min_num_edges=0, max_num_edges=0,
                                delete_not_connected_nodes=True):
        """
        Generates a random networks.

        :param seed: network seed
        :param min_num_nodes: minimum number of nodes
        :param max_num_nodes: maximum number of nodes
        :param min_num_edges: minimum number of edges
        :param max_num_edges: maximum number of edges
        :param delete_not_connected_nodes: removes unconnected nodes
        """
        self.model_facade.generate_random_network_in_new_model(seed, min_num_nodes, max_num_nodes, min_num_edges,
                                                               max_num_edges, delete_not_connected_nodes)
