from utils.utils import OS
import sys

if OS.Linux:
    import matplotlib

    matplotlib.use("agg")
import json
import math
import multiprocessing
import random
from multiprocessing import Pool
from threading import Thread
from typing import Union, Callable
from uuid import UUID

import networkx

from Model.Computation import Computation
from Model.GraphLayoutAlgorithm import GraphLayoutAlgorithm
from Model.Network.Edge import Edge
from Model.Network.Flow import Flow
from Model.Network.Network import Network
from Model.Network.Node import Node
from Model.Result import Result
from utils import utils


class ModelFacade:
    def __init__(self, network: Network = None):
        self.computation_pools = {}
        self.pending_results = {}
        if network is None:
            network = Network(model=self)
        self.network = network

    def add_node(self, x: int = 0, y: int = 0, name: str = None, is_selected=False, uid=None) -> Node:
        """
        Adds a node to the model.

        :param x: x coordinate
        :param y: y coordinate
        :param name: node name
        :param is_selected: selection state
        :param uid: UID
        :return: node object
        """
        if name is None:
            name = f"S{self.network.node_counter}"

        node = Node(name=str(name), is_selected=is_selected, x=x, y=y, uid=uid)
        self.network.node_counter += 1
        self.network.add_node(node)
        self.network.notify((node, "add_node"))

        return node

    def add_edge(self, start_node: Node, end_node: Node, name=None, is_selected=False, uid=None) -> Edge:
        """
        Adds an edge to the model.

        :param start_node: start node
        :param end_node: end node
        :param name: edge name
        :param is_selected: selection state
        :param uid: UID
        :return: edge object
        """
        try:
            if start_node is end_node:
                raise ValueError("start node equals end node")
            if end_node in start_node.edges or start_node in end_node.edges:
                raise ValueError("edge already exists")
        except ValueError as e:
            self.notify_error(e)
            raise e

        if name is None:
            name = f"E{self.network.edge_counter}"

        edge = Edge(name=name, is_selected=is_selected, start_node=start_node, end_node=end_node, uid=uid)
        self.network.edge_counter += 1
        self.network.add_edge(edge)
        self.network.notify((edge, "add_edge"))
        start_node.notify((edge, "add_edge"))
        end_node.notify((edge, "add_edge"))

        return edge

    def add_flow(self, path: list[Node], name=None, is_selected=False, uid=None) -> Flow:
        """
        Adds a flow to the model.

        :param path: path of the flow
        :param name: flow name
        :param is_selected: selection state
        :param uid: UID
        :return: flow object
        """
        if name is None:
            name = f"F{self.network.flow_counter}"
        try:
            if len(path) < 2:
                raise ValueError("Path too short")
        except ValueError as e:
            self.notify_error(e)
            raise e

        self.add_missing_edges_to_path(path, is_selected=is_selected)

        flow = Flow(name=name, is_selected=is_selected, path=path, uid=uid)
        self.network.flow_counter += 1
        self.network.add_flow(flow)

        self.network.notify((flow, "add_flow"))
        for node in path:
            node.notify((flow, "add_flow"))
        return flow

    def add_missing_edges_to_path(self, path: list[Node], is_selected=False):
        """
        Adds edges to the model based on the given path.

        :param path: flow path
        :param is_selected: selection state of the edges
        """
        for index, start_node in enumerate(path):
            if index + 1 == len(path):
                return
            end_node = path[index + 1]
            if end_node not in start_node.edges:
                self.add_edge(start_node, end_node, is_selected=is_selected)

    def select_component(self, component: Union[Node, Edge, Flow], activity):
        """
        Sets the selection state of a component.

        :param component: component object
        :param activity: selection state
        """
        if component.is_selected != activity:
            if activity:
                self.network.selected_components.append(component)
            else:
                self.network.selected_components.remove(component)
            component.is_selected = activity
            component.notify((component, "set_selection"))

    def unselect_all_components(self):
        """
        Deselects every component of the model.
        """
        for component in self.network.selected_components:
            component.is_selected = False
            component.notify((component, "set_selection"))
        self.network.selected_components.clear()

    def delete_component(self, component: Union[Node, Edge, Flow]):
        """
        Deletes a component from the model.

        :param component: component object
        """
        if isinstance(component, Node):
            self.network.delete_node(component)
        elif isinstance(component, Edge):
            self.network.delete_edge(component)
        elif isinstance(component, Flow):
            self.network.delete_flow(component)

    def add_configuration(self, network_configuration_class, name=None) -> type['AbstractNetworkConfiguration']:
        """
        Adds a configuration to the model.

        :param network_configuration_class: a network configuration class
        :param name: configuration name
        :return: instance of a network configuration
        """
        if name is None:
            name = f"{network_configuration_class.get_configuration_name()}-{self.network.configs_counter}"
        self.network.configs_counter += 1
        flow_ids_of_interest = list(self.network.flows.keys())
        network_configuration = network_configuration_class(name=name, flow_ids_of_interest=flow_ids_of_interest,
                                                            model=self, associated_component=self.network)
        group_id = network_configuration.group_id
        self.network.configurations[group_id] = network_configuration
        self.network.notify((network_configuration, "add_configuration"))

        node_configuration_class = network_configuration_class.get_node_configuration_class()
        for node in self.network.nodes.values():
            node.configurations[group_id] = node_configuration_class(group_id=group_id, model=self,
                                                                     associated_component=node)
            node.notify((node.configurations[group_id], "add_configuration"))

        edge_configuration_class = network_configuration_class.get_edge_configuration_class()
        for edge in self.network.edges.values():
            edge.configurations[group_id] = edge_configuration_class(group_id=group_id, model=self,
                                                                     associated_component=edge)
            edge.notify((edge.configurations[group_id], "add_configuration"))

        flow_configuration_class = network_configuration_class.get_flow_configuration_class()
        for flow in self.network.flows.values():
            flow.configurations[group_id] = flow_configuration_class(group_id=group_id, model=self,
                                                                     associated_component=flow)
            flow.notify((flow.configurations[group_id], "add_configuration"))
        return network_configuration

    def delete_configuration(self, configuration):
        """
        Deletes a network configuration from the model.

        :param configuration: configuration object
        """
        group_id = configuration.group_id
        if group_id in self.network.configurations:
            for flow in self.network.flows.values():
                del flow.configurations[group_id]
                flow.notify((group_id, "delete_configuration"))
            for edge in self.network.edges.values():
                del edge.configurations[group_id]
                edge.notify((group_id, "delete_configuration"))
            for node in self.network.nodes.values():
                del node.configurations[group_id]
                node.notify((group_id, "delete_configuration"))
            del self.network.configurations[group_id]
            self.network.notify((group_id, "delete_configuration"))

    def update_network_name(self, name: str):
        """
        Updates the network name.

        :param name: new name
        """
        self.network.update_name(name)

    def update_network_information(self, new_text: str):
        """
        Updates the network information.

        :param new_text: new information text
        """
        self.network.information_text = new_text
        self.network.notify((self.network, "information_text"))

    @staticmethod
    def update_node_name(node: Node, name: str):
        """
        Updates the name of a node.

        :param node: node object
        :param name: new name
        """
        node.name = name
        node.notify((node, "set_parameter"))

    @staticmethod
    def update_node_x_y(node: Node, x: int, y: int):
        """
        Updates the x and y coordinates of a node.

        :param node: node object
        :param x: x coordinate
        :param y: y coordinate
        """
        node.x = x
        node.y = y
        node.notify((node, "set_parameter"))

    @staticmethod
    def update_edge_name(edge: Edge, name: str):
        """
        Updates the name of an edge.

        :param edge: edge object
        :param name: new name
        """
        edge.name = name
        edge.notify((edge, "set_parameter"))

    @staticmethod
    def update_flow_name(flow: Flow, name: str):
        """
        Updates the name of a flow.

        :param flow: flow object
        :param name: new name
        """
        flow.name = name
        flow.notify((flow, "set_parameter"))

    def insert_node_in_flow_path(self, flow: Flow, node: Node, index: int = None, is_edge_selected=False):
        """
        Inserts a node to an existing path at a specific index.

        :param flow: flow object
        :param node: node object
        :param index: insertion index, use 'None' to append
        :param is_edge_selected: selection state of the edge
        """
        if index is None:
            self.append_node_to_flow_path(flow, node, is_edge_selected=is_edge_selected)
        else:
            flow.path.insert(index, node)
            try:
                self.add_missing_edges_to_path(flow.path, is_selected=is_edge_selected)
            except Exception as e:
                flow.path.remove(node)
                raise e
            flow.notify((flow, "update_path"))

    def append_node_to_flow_path(self, flow: Flow, node: Node, is_edge_selected=False):
        """
        Appends a node to an existing flow path.

        :param flow: flow object
        :param node: node object
        :param is_edge_selected: selection state of the edge
        """
        if node not in flow.path[-1].edges:
            self.add_edge(flow.path[-1], node, is_selected=is_edge_selected)
        flow.path.append(node)
        flow.notify((flow, "update_path"))

    def update_flow_color(self, flow: Flow, color: str):
        """
        Update the color of a flow.

        :param flow: flow object
        :param color: color as RGB string (#RRGGBB)
        """
        self.check_valid_color(color)
        flow.color = color
        flow.notify((flow, "set_parameter"))

    def update_flow_highlight_color(self, flow: Flow, highlight_color: str):
        """
        Update the highlight color of a flow.

        :param flow: flow object
        :param highlight_color: color as RGB string (#RRGGBB)
        """
        self.check_valid_color(highlight_color)
        flow.highlight_color = highlight_color
        flow.notify((flow, "set_parameter"))

    def run_computation(self, number_of_workers=None) -> Computation:
        """
        Runs the computation with the current configurations.

        :param number_of_workers: number of processes
        :return: instance of a computation
        """
        active_configurations = list(filter(lambda c: c.is_active, self.network.configurations.values()))
        sys.setrecursionlimit(900000)
        active_configurations = list(filter(lambda c: c.is_active, list(self.network.configurations.values())))
        if len(active_configurations) == 0 or not self.network.flows:
            raise ValueError("No active configuration or no flows")

        def on_error(error, error_result):
            error_result.error()
            self.notify_error(error)

        def make_error_callback(error_result):
            return lambda error: on_error(error, error_result)

        if number_of_workers is None:
            process_count = min(multiprocessing.cpu_count(), len(active_configurations))
        else:
            process_count = number_of_workers
        computation = Computation()
        if OS.Linux:
            try:
                multiprocessing.set_start_method('spawn')
            except RuntimeError:
                pass
        self.computation_pools[computation] = pool = Pool(processes=process_count)
        for configuration in active_configurations:
            result = Result(configuration_name=configuration.name, configuration_id=configuration.group_id)
            self.pending_results[result.id] = result
            computation.add_result(result)

            pool.apply_async(self._compute_configuration, (configuration, result),
                             callback=self._notify_result,
                             error_callback=make_error_callback(result))
        computation.start()
        self.network.notify((computation, "computation_started"))
        Thread(target=lambda: (pool.close(), pool.join(), self._end_computation(computation))).start()
        return computation

    def _compute_configuration(self, configuration, result: Result):
        """
        Computes a configuration.

        :param configuration: configuration object
        :param result: result object to store results
        :return: result object
        """
        result.start()
        configuration.compute(self.network, result)
        result.finish()
        return result

    def _end_computation(self, computation: Computation):
        """
        Ends the computation.

        :param computation: computation object
        """
        computation.finish()
        if computation in self.computation_pools:
            del self.computation_pools[computation]

    def cancel_computation(self, computation: Computation):
        """
        Cancels a running computation.

        :param computation: computation object
        """
        computation.cancel()
        if computation in self.computation_pools:
            self.computation_pools[computation].terminate()

    def _notify_result(self, pickled_result: Result):
        """
        Notify the subscribers of the result object about finishing the computation.

        :param pickled_result: includes the computation results
        """
        original_result = self.pending_results[pickled_result.id]
        original_result.__dict__ = original_result.__dict__ | pickled_result.__dict__
        original_result.notify((original_result, "finished_result"))
        del self.pending_results[pickled_result.id]

    def update_configuration_parameters(self, configuration, dictionary: dict):
        """
        Updates parameters of a configuration.

        :param configuration: configuration object
        :param dictionary: parameter dictionary
        """
        try:
            configuration.update_parameter_dict(dictionary)
        except Exception as error:
            self.notify_error(error)
            raise error
        finally:
            configuration.notify((configuration, "set_parameter"))

    def update_configuration_name(self, group_id: UUID, new_name: str):
        """
        Updates the name of a configuration.

        :param group_id: group ID of the configuration
        :param new_name: new name
        """
        configuration = self.network.configurations[group_id]
        configuration.name = new_name
        configuration.notify((configuration, "set_parameter"))

        for flow in self.network.flows.values():
            configuration = flow.configurations[group_id]
            configuration.notify((configuration, "set_parameter"))

        for edge in self.network.edges.values():
            configuration = edge.configurations[group_id]
            configuration.notify((configuration, "set_parameter"))

        for node in self.network.nodes.values():
            configuration = node.configurations[group_id]
            configuration.notify((configuration, "set_parameter"))

    def add_flow_of_interest(self, group_id: UUID, flow: Flow):
        """
        Adds a flow of interest to a list of flow of interests.

        :param group_id: group ID of a configuration
        :param flow: flow object
        """
        configuration = self.network.configurations[group_id]
        if flow.id not in configuration.flow_ids_of_interest:
            configuration.flow_ids_of_interest.append(flow.id)
            configuration.notify((configuration, "set_parameter"))

            flow_configuration = flow.configurations[group_id]
            flow_configuration.is_flow_of_interest = True
            flow_configuration.notify((flow_configuration, "set_parameter"))

    def remove_flow_of_interest(self, group_id: UUID, flow: Flow):
        """
        Removes a flow of interest from a list of flow of interests.

        :param group_id: group ID of a configuration
        :param flow: flow object
        """
        configuration = self.network.configurations[group_id]
        if flow.id in configuration.flow_ids_of_interest:
            configuration.flow_ids_of_interest.remove(flow.id)
            configuration.notify((configuration, "set_parameter"))

            flow_configuration = flow.configurations[group_id]
            flow_configuration.is_flow_of_interest = False
            flow_configuration.notify((flow_configuration, "set_parameter"))

    def notify_error(self, error: Exception):
        """
        Notify the subscribers of the network about an error.

        :param error: error
        """
        utils.print_exception_traceback(error)
        self.network.notify((error, "error"))

    def import_network(self, json_file: str):
        """
        Imports a network from a JSON file.

        :param json_file: JSON file
        """
        try:
            new_model = ModelFacade.load_network(json_file)
        except Exception as e:
            self.notify_error(e)
            return
        self.network.notify((new_model, "new_model"))

    def generate_random_network_in_new_model(self, seed=None, min_num_nodes=100, max_num_nodes=150, min_num_edges=200,
                                             max_num_edges=200, delete_not_connected_nodes=True) -> 'ModelFacade':
        """
        Generates a network and returns a new model.

        :param seed: network seed
        :param min_num_nodes: minimum number of nodes
        :param max_num_nodes: maximum number of nodes
        :param min_num_edges: minimum number of edges
        :param max_num_edges: maximum number of edges
        :param delete_not_connected_nodes: whether unconnected node should be removed
        :return: model
        """
        rand = random.Random(seed)
        model = ModelFacade(network=Network(network_id=UUID(bytes=rand.randbytes(16), version=4)))
        used_nodes = set()
        num_nodes = rand.randint(min_num_nodes, max_num_nodes)
        column_num = int(math.sqrt(num_nodes))
        y = -1
        for i in range(num_nodes):
            x = i % column_num
            if x == 0:
                y += 1
            model.add_node(x * 200, y * 200, uid=UUID(bytes=rand.randbytes(16), version=4))
        all_nodes = list(model.network.nodes.values())

        num_edges = rand.randint(min_num_edges, max_num_edges)
        for i in range(num_edges):
            node_i = rand.choice(all_nodes)
            node_j = rand.choice(all_nodes)
            while node_j == node_i:
                node_j = rand.choice(all_nodes)
            try:
                if node_j not in node_i.edges and node_i not in node_j.edges:
                    model.add_edge(node_i, node_j, uid=UUID(bytes=rand.randbytes(16), version=4))
                    used_nodes.add(node_i)
                    used_nodes.add(node_j)
            except ValueError:
                continue

        if delete_not_connected_nodes:
            for node in used_nodes.symmetric_difference(model.network.nodes.values()):
                model.delete_component(node)

        self.network.notify((model, "new_model"))
        return model

    def generate_networkx_network_in_new_model(self, generator: Callable[..., networkx.Graph], uid_seed=None,
                                               **kwargs) -> 'ModelFacade':
        """
        Generates a network using NetworkX and returns a new model.

        :param generator: NetworkX generation function
        :param uid_seed: seed to recreate UIDs of network components
        :param kwargs: arguments for the NetworkX generation function
        :return: model
        """
        uid_rand = random.Random(uid_seed)
        try:
            graph: networkx.Graph = generator(**kwargs)
            scale = ModelFacade._get_layout_scale(graph)
            pos = networkx.kamada_kawai_layout(graph, scale=scale)

            model = ModelFacade()
            mapping = {}
            for nx_node in graph.nodes:
                x, y = pos[nx_node]
                node = model.add_node(x=x, y=y, name=nx_node, uid=UUID(bytes=uid_rand.randbytes(16), version=4))
                mapping[nx_node] = node
            for (i, j) in graph.edges:
                node_i, node_j = mapping[i], mapping[j]
                model.add_edge(node_i, node_j, uid=UUID(bytes=uid_rand.randbytes(16), version=4))
        except Exception as e:
            self.notify_error(e)
            raise e
        self.network.notify((model, "new_model"))
        return model

    def add_random_flows(self, min_num_flows=5, max_num_flows=10, min_num_nodes_in_flow_path=2,
                         max_num_nodes_in_flow_path=10,
                         flow_seed=None):
        """
        Adds random flows to a network.

        :param min_num_flows: minimum number of flows
        :param max_num_flows: maximum number of flows
        :param min_num_nodes_in_flow_path: minimum number of nodes in a flow path
        :param max_num_nodes_in_flow_path: maximum number of nodes in a flow path
        :param flow_seed: flow seed
        """
        if min_num_nodes_in_flow_path < 2 or max_num_nodes_in_flow_path < 2:
            raise ValueError("Minimal 2 nodes needed for flow")

        graph = self.make_networkx_graph()
        nodes = list(self.network.nodes.values())

        rand = random.Random(flow_seed)
        target_num_flows = rand.randint(min_num_flows, max_num_flows)
        failed_combinations = set()
        max_combinations = len(nodes) ** 2 * (max_num_nodes_in_flow_path - min_num_nodes_in_flow_path + 1)
        added_flows = 0
        while added_flows < target_num_flows:
            start_node = rand.choice(nodes)
            end_node = rand.choice(nodes)
            path_length = rand.randint(min_num_nodes_in_flow_path, max_num_nodes_in_flow_path)
            if start_node == end_node:
                failed_combinations.add((start_node, end_node, path_length))
            if len(failed_combinations) == max_combinations:
                raise ValueError(
                    f"Cannot find a simple path with length " +
                    f"[{min_num_nodes_in_flow_path}, {max_num_nodes_in_flow_path}]")
            while (start_node, end_node, path_length) in failed_combinations:
                start_node = rand.choice(nodes)
                end_node = rand.choice(nodes)
                path_length = rand.randint(min_num_nodes_in_flow_path, max_num_nodes_in_flow_path)
            found_path = None
            for path in networkx.all_simple_paths(graph, start_node, end_node, cutoff=path_length):
                if len(path) == path_length:
                    found_path = path
                    break
            if found_path is None:
                failed_combinations.add((start_node, end_node, path_length))
                continue
            self.add_flow(path=found_path, uid=UUID(bytes=rand.randbytes(16), version=4))
            added_flows += 1

    def make_networkx_graph(self) -> networkx.Graph:
        """
        Translates a network into a NetworkX graph.

        :return: NetworkX graph
        """
        graph = networkx.Graph()
        graph.add_nodes_from(self.network.nodes.values())
        edges = self.network.edges.values()
        starts = map(lambda e: e.start, edges)
        ends = map(lambda e: e.end, edges)
        graph.add_edges_from(zip(starts, ends))
        return graph

    def change_graph_layout(self, layout: GraphLayoutAlgorithm = GraphLayoutAlgorithm.fruchterman_reingold):
        """
        Changes the layout of the network using NetworkX.

        :param layout: NetworkX layout type
        """
        G = networkx.Graph()
        initial_pos = {}
        for node_id, node in self.network.nodes.items():
            G.add_node(node_id)
            initial_pos[node_id] = node.x, node.y
        for edge in self.network.edges.values():
            G.add_edge(edge.start.id, edge.end.id)

        scale = ModelFacade._get_layout_scale(G)

        try:
            if layout == GraphLayoutAlgorithm.fruchterman_reingold:
                pos = networkx.fruchterman_reingold_layout(G, k=scale, pos=initial_pos, scale=scale)
            elif layout == GraphLayoutAlgorithm.planar:
                pos = networkx.planar_layout(G, scale=scale * 1.5)
            elif layout == GraphLayoutAlgorithm.shell:
                pos = networkx.shell_layout(G, scale=scale)
            elif layout == GraphLayoutAlgorithm.kamada_kawai:
                pos = networkx.kamada_kawai_layout(G, pos=initial_pos, scale=scale)
            elif layout == GraphLayoutAlgorithm.spectral:
                pos = networkx.spectral_layout(G, scale=scale)
            elif layout == GraphLayoutAlgorithm.spiral:
                pos = networkx.spiral_layout(G, scale=scale)
            elif layout == GraphLayoutAlgorithm.circular:
                pos = networkx.circular_layout(G, scale=scale)
            elif layout == GraphLayoutAlgorithm.random:
                pos = networkx.random_layout(G)
                for node_id, coord in pos.items():
                    pos[node_id] = scale * coord
            else:
                raise ValueError("Unknown Algorithm")
        except Exception as e:
            self.notify_error(e)
            raise e

        for node_id, (x, y) in pos.items():
            node = self.network.nodes[node_id]
            self.update_node_x_y(node, int(x), int(y))

    @staticmethod
    def _get_layout_scale(G: networkx.Graph):
        """
        Returns the scale of the NetworkX graph.

        :param G: NetworkX graph
        :return: scale
        """
        num_components = G.number_of_nodes() + G.number_of_edges()
        base = 1.07
        if num_components <= 20:
            x = math.log(num_components, base)
        elif num_components <= 50:
            x = math.log(num_components, base - 0.03)
        elif num_components <= 100:
            x = math.log(num_components, base - 0.04)
        elif num_components <= 500:
            x = math.log(num_components, base - 0.05)
        else:
            x = math.log(num_components, base - 0.06)
        return x * 10

    def _get_flows_as_networkx_digraph(self):
        """
        Creates a digraph containing flows.

        :return: NetworkX digraph
        """
        g = networkx.DiGraph()
        flow: Flow
        for flow in self.network.flows.values():
            for index, node_i in enumerate(flow.path):
                if index + 1 == len(flow.path):
                    break
                g.add_edge(node_i, flow.path[index + 1])
        return g

    def are_flows_cyclic(self):
        """
        Checks whether the network contains cyclic flows.

        :return: whether flows are cyclic
        """
        g = self._get_flows_as_networkx_digraph()
        return not networkx.is_directed_acyclic_graph(g)

    def get_flow_cycles(self):
        """
        Returns cyclic flows.

        :return: simple cycles as defined by NetworkX
        """
        g = self._get_flows_as_networkx_digraph()
        return networkx.simple_cycles(g)

    def export_network(self, path: str):
        """
        Exports the network as JSON file.

        :param path: path to the JSON file
        """
        with open(path, 'w') as f:
            json_string = self.network.to_json()
            f.write(json_string)

    @staticmethod
    def load_network(path: str):
        """
        Loads a network from a JSON file.

        :param path: path to the JSON file
        :return: the network model
        """
        with open(path) as json_file:
            json_dict = json.load(json_file)
        model = ModelFacade()
        network = Network.from_json(json_dict, model)
        model.network = network
        return model

    def check_valid_color(self, color: str):
        """
        Checks whether a color is in a valid RGB format.

        :param color: color string
        :return: whether string is valid
        """
        try:
            if len(color) != 7:
                raise ValueError()
            int(color[1:7], 16)
        except ValueError:
            e = ValueError(f"Illegal Color: \"{color}\". Expected \"#rrggbb\" format.")
            self.notify_error(e)
            raise e

    def __getstate__(self):
        """
        Used to pickle the object for process communication

        :return: network dictionary
        """
        return {"network": self.network}
