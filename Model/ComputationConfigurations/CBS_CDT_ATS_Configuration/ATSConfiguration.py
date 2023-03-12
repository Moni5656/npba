import uuid
from typing import Type

import matplotlib.figure
import numpy as np
import scienceplots
from matplotlib import pyplot as plt

from ComputationMethods.CBS_CDT_ATS import CBS, Flow as ATS_flow, Link as ATS_link
from Model.ComputationConfigurations.CBS_CDT_ATS_Configuration.EdgeConfiguration import EdgeConfiguration
from Model.ComputationConfigurations.CBS_CDT_ATS_Configuration.FlowConfiguration import FlowConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractNetworkConfiguration import \
    AbstractNetworkConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultNodeConfiguration import DefaultNodeConfiguration
from Model.Result import Result


class ATSConfiguration(AbstractNetworkConfiguration):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_configuration_information() -> str:
        return "CBS-CDT-ATS: E. Mohammadpour, E. Stai, M. Mohiuddin, and J.-Y. Le Boudec. \"Latency and Backlog " \
               "Bounds in Time-Sensitive Networking with Credit Based Shapers and Asynchronous Traffic Shaping.\" In " \
               "2018 30th International Teletraffic Congress (ITC 30), volume 2, pages 1–6. IEEE, 2018."

    @staticmethod
    def get_configuration_name() -> str:
        return "CBS-CDT-ATS"

    @staticmethod
    def get_configuration_identifier() -> str:
        return "CBS-CDT-ATS"

    @staticmethod
    def get_node_configuration_class() -> Type[DefaultNodeConfiguration]:
        return DefaultNodeConfiguration

    @staticmethod
    def get_edge_configuration_class() -> Type[EdgeConfiguration]:
        return EdgeConfiguration

    @staticmethod
    def get_flow_configuration_class() -> Type[FlowConfiguration]:
        return FlowConfiguration

    def compute(self, network, result: Result):
        plt.style.use(["science"])
        plt.rcParams.update({'figure.dpi': '150'})
        _ = scienceplots.inode  # avoid unused import warning

        self._compute_args["result"] = result
        self._compute_args["network"] = network

        result.set_start_time()
        self.make_computation_model(network)

        self._compute_end_to_end_delay()
        result.append_result("Response time:")
        self._compute_response_time_ir()
        self._compute_response_time_link()
        result.append_result("Backlog:")
        self._compute_backlog_link()
        self._compute_backlog_ir()
        result.set_end_time()

        self._make_plots()

    def make_computation_model(self, network):
        """
        Translates a given network into an ATS-CBS network.

        :param network: network object
        """
        links = {}
        for edge in network.edges.values():
            configuration = edge.configurations[self.group_id]
            i, j = edge.start.id, edge.end.id
            links[i, j] = ATS_link(str(i), str(j), configuration.link_speed * 10 ** 6,
                                   configuration.idle_slope_A * 10 ** 6,
                                   configuration.send_slope_A * 10 ** 6, configuration.idle_slope_B * 10 ** 6,
                                   configuration.send_slope_B * 10 ** 6, configuration.t_var_min,
                                   configuration.t_var_max, configuration.t_proc_min, configuration.t_proc_max)
            links[j, i] = ATS_link(str(j), str(i), configuration.link_speed * 10 ** 6,
                                   configuration.idle_slope_A * 10 ** 6,
                                   configuration.send_slope_A * 10 ** 6, configuration.idle_slope_B * 10 ** 6,
                                   configuration.send_slope_B * 10 ** 6, configuration.t_var_min,
                                   configuration.t_var_max, configuration.t_proc_min, configuration.t_proc_max)

        flow_mapping = {}
        for flow in network.flows.values():
            config = flow.configurations[self.group_id]
            path = []
            for index, node_i in enumerate(flow.path):
                if index + 1 >= len(flow.path):
                    break
                node_j = flow.path[index + 1]
                link_i_j = links[node_i.id, node_j.id]
                path.append(link_i_j)

            flow_mapping[flow.id] = ATS_flow(config.regulation_rate * 10 ** 6, config.l_min * 10 ** 6,
                                             config.l_max * 10 ** 6, path, config.type, config.ac_type)
        cbs = CBS(list(flow_mapping.values()))
        self._compute_args["cbs"] = cbs
        self._compute_args["flow_mapping"] = flow_mapping
        self._compute_args["link_mapping"] = links

    def _compute_end_to_end_delay(self):
        """
        Computes the end-to-end delay for every flow of interest.
        """
        network = self._compute_args["network"]
        result = self._compute_args["result"]
        flow_mapping = self._compute_args["flow_mapping"]
        cbs = self._compute_args["cbs"]

        names_a = []
        names_b = []
        values_a = []
        values_b = []
        result_text = ""
        for flow_id in self.flow_ids_of_interest:
            ats_flow = flow_mapping[flow_id]
            if ats_flow.t == "CDT" or ats_flow.t == "BE":
                continue
            delay = cbs.end_to_end_delay(ats_flow)
            flow_name = network.flows[flow_id].name
            result_text += f"Flow {flow_name}: {str(delay)}s\n"
            if ats_flow.t == "A":
                names_a.append(flow_name)
                values_a.append(delay)
            else:
                names_b.append(flow_name)
                values_b.append(delay)

        result.append_result("End-to-End Delay:")
        result.append_result(result_text, 1)
        self._compute_args["e2e"] = names_a, values_a, names_b, values_b

    def _compute_backlog_link(self):
        """
        Computes the backlog bounds for used links.
        """
        network = self._compute_args["network"]
        result = self._compute_args["result"]
        result_text_a, names, values_a = self._compute_backlog_for_class(network, "A")
        result_text_b, _, values_b = self._compute_backlog_for_class(network, "B")

        result.append_result("Backlog for class A:", 1)
        result.append_result(result_text_a, 2)
        result.append_result("Backlog for class B:", 1)
        result.append_result(result_text_b, 2)

        self._compute_args["backlog_link"] = names, values_a, values_b

    def _compute_backlog_for_class(self, network, traffic_class="A"):
        """
        Computes the backlog for a specific traffic class.

        :param network: network object
        :param traffic_class: "A" or "B"
        :return: (result string, link names, backlog bounds)
        """
        cbs = self._compute_args["cbs"]
        names = []
        values = []
        result = ""
        for (name, link) in self._get_used_links(network):
            backlog = cbs.backlog_cbfs(traffic_class, link)
            result += f"{name}: {backlog} bit\n"
            names.append(name)
            values.append(backlog)
        return result, names, values

    def _compute_backlog_for_interleaved_regulator(self, network, flow):
        """
        Computes the backlog bounds at every passed interleaved regulator of a flow.

        :param network: network object
        :param flow: flow object
        :return: result string
        """
        flow_mapping = self._compute_args["flow_mapping"]
        cbs = self._compute_args["cbs"]
        result = ""
        ats_flow = flow_mapping[flow.id]
        for index, link_i_j in enumerate(ats_flow.p):
            if index + 1 >= len(ats_flow.p):
                break
            link_j_k = ats_flow.p[index + 1]
            name_i = network.nodes[uuid.UUID(link_i_j.i)].name
            name_j = network.nodes[uuid.UUID(link_i_j.j)].name
            name_k = network.nodes[uuid.UUID(link_j_k.j)].name
            backlog = cbs.backlog_interleaved_regulator(ats_flow, link_i_j, link_j_k)
            result += f"{name_i}-{name_j}-{name_k}: {backlog} bit\n"
        return result

    def _compute_response_time_for_interleaved_regulator(self, network, flow):
        """
        Computes the response time at every interleaved regulator of a flow.

        :param network: network object
        :param flow: flow object
        :return: result string
        """
        flow_mapping = self._compute_args["flow_mapping"]
        cbs = self._compute_args["cbs"]
        result = ""
        ats_flow = flow_mapping[flow.id]
        for index, link_i_j in enumerate(ats_flow.p):
            if index + 1 >= len(ats_flow.p):
                break
            link_j_k = ats_flow.p[index + 1]
            name_i = network.nodes[uuid.UUID(link_i_j.i)].name
            name_j = network.nodes[uuid.UUID(link_i_j.j)].name
            name_k = network.nodes[uuid.UUID(link_j_k.j)].name
            response_time = cbs.h_i_j_k(ats_flow, link_i_j, link_j_k)
            result += f"{name_i}-{name_j}-{name_k}: {response_time} s\n"
        return result

    def _compute_response_time_for_link(self, network, flow):
        """
        Computes the response time for every passed link of a flow.

        :param network: network object
        :param flow: flow object
        :return: result string
        """
        flow_mapping = self._compute_args["flow_mapping"]
        cbs = self._compute_args["cbs"]
        result = ""
        ats_flow = flow_mapping[flow.id]
        for index, link_i_j in enumerate(ats_flow.p):
            name_i = network.nodes[uuid.UUID(link_i_j.i)].name
            name_j = network.nodes[uuid.UUID(link_i_j.j)].name
            response_time = cbs.s_i_j(ats_flow, link_i_j)
            result += f"{name_i}-{name_j}: {response_time} s\n"
        return result

    def _get_used_links(self, network):
        """
        Returns a list of used links of a network.

        :param network: network object
        :return: a sorted list of used links
        """
        link_mapping = self._compute_args["link_mapping"]
        used_links = {}
        for flow_id in self.flow_ids_of_interest:
            flow = network.flows[flow_id]
            for index, node_i in enumerate(flow.path):
                if index + 1 >= len(flow.path):
                    break
                node_j = flow.path[index + 1]
                link = link_mapping[node_i.id, node_j.id]
                name = f"{node_i.name}-{node_j.name}"
                used_links[name] = link
        return sorted(zip(used_links.keys(), used_links.values()), key=lambda name_link: name_link[0])

    def _compute_response_time_ir(self):
        """
        Computes the response time of interleaved regulators for every flow of interest.
        """
        network = self._compute_args["network"]
        result = self._compute_args["result"]

        result.append_result("Response time for interleaved regulator:", 1)
        for flow_id in self.flow_ids_of_interest:
            flow = network.flows[flow_id]
            result.append_result(f"Flow {flow.name}:", 2)
            result.append_result(
                self._compute_response_time_for_interleaved_regulator(network, flow), 3)

    def _compute_response_time_link(self):
        """
        Computes the response time at every link for every flow of interest.
        """
        network = self._compute_args["network"]
        result = self._compute_args["result"]
        result.append_result("Response time for link:", 1)
        for flow_id in self.flow_ids_of_interest:
            flow = network.flows[flow_id]
            result.append_result(f"Flow {flow.name}:", 2)
            result.append_result(self._compute_response_time_for_link(network, flow), 3)

    def _compute_backlog_ir(self):
        """
        Computes the backlog bounds of interleaved regulators for every flow of interest.
        """
        network = self._compute_args["network"]
        result = self._compute_args["result"]
        result.append_result("Backlog for interleaved regulator:", 1)
        for flow_id in self.flow_ids_of_interest:
            flow = network.flows[flow_id]
            result.append_result(f"Flow {flow.name}:", 2)
            result.append_result(
                self._compute_backlog_for_interleaved_regulator(network, flow), 3)

    def _make_plots(self):
        """
        Creates plots based on the delay and backlog bounds.
        """
        names_a, values_a, names_b, values_b = self._compute_args["e2e"]
        if len(names_a) + len(names_b) < 50:
            self.e2e_bar_chart(names_a, values_a, names_b, values_b)
        self.e2e_boxplot(values_a, values_b)

        names, values_a, values_b = self._compute_args["backlog_link"]
        if len(names) < 50:
            self.class_backlog_bar_chart(names, values_a, values_b)
        self.class_backlog_boxplot(values_a, values_b)

    def e2e_boxplot(self, values_a, values_b):
        """
        Creates a boxplot based on the end-to-end delay of class A and B flows.

        :param values_a: end-to-end delays of class A flows
        :param values_b: end-to-end delays of class B flows
        """
        fig: matplotlib.figure.Figure = plt.figure()
        axe: matplotlib.figure.Axes = fig.add_subplot(111)
        data = [values_a, values_b]
        labels = ["Class A", "Class B"]
        axe.boxplot(data, labels=labels)
        axe.set_xlabel("Flows")
        axe.set_ylabel("End-to-End Delay (s)")
        result = self._compute_args["result"]
        result.add_plot(fig, "Aggregated Delays")

    def e2e_bar_chart(self, names_a, values_a, names_b, values_b):
        """
        Creates a bar chart based on the end-to-end delays of class A and B flows.

        :param names_a: names of the class A flows
        :param values_a: end-to-end delays of class A flows
        :param names_b: names of the class B flows
        :param values_b: end-to-end delays of class B flows
        """
        fig: matplotlib.figure.Figure = plt.figure()
        axe: matplotlib.figure.Axes = fig.add_subplot(111)
        axe.bar(names_a, values_a, label="Class A")
        axe.bar(names_b, values_b, label="Class B")
        axe.set_xlabel("Flows")
        axe.set_ylabel("End-to-End Delay (s)")
        axe.legend()
        result = self._compute_args["result"]
        result.add_plot(fig, "End-to-End Delay")

    def class_backlog_boxplot(self, values_a, values_b):
        """
        Creates a boxplot based on the backlog bounds of class A and B flows.

        :param values_a: backlog bounds of class A flows
        :param values_b: backlog bounds of class B flows
        """
        fig: matplotlib.figure.Figure = plt.figure()
        axe: matplotlib.figure.Axes = fig.add_subplot(111)
        data = [values_a, values_b]
        labels = ["Class A", "Class B"]
        axe.boxplot(data, labels=labels)
        axe.set_xlabel("Edges")
        axe.set_ylabel("Backlog (bit)")
        result = self._compute_args["result"]
        result.add_plot(fig, "Aggregated Backlogs")

    def class_backlog_bar_chart(self, names, values_a, values_b):
        """
        Creates a bar plot based on the backlog bounds of class A and B flows.

        :param names: link names
        :param values_a: backlog bounds of class A flows
        :param values_b: backlog bounds of class B flows
        """
        fig: matplotlib.figure.Figure = plt.figure()
        axe: matplotlib.figure.Axes = fig.add_subplot(111)
        x_index = np.arange(len(names))
        axe.bar(x_index - 0.2, values_a, 0.4, label="Class A")
        axe.bar(x_index + 0.2, values_b, 0.4, label="Class B")
        axe.set_xticks(ticks=x_index)
        axe.set_xticklabels(names)
        axe.set_xlabel("Edges")
        axe.set_ylabel("Backlog (bit)")
        axe.legend()
        result = self._compute_args["result"]
        result.add_plot(fig, "Backlog")
