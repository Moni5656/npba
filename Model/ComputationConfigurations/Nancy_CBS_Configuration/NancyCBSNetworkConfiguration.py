from fractions import Fraction
from multiprocessing import Process
from typing import Type
from uuid import UUID

import numpy as np
import scienceplots
from matplotlib import pyplot as plt

from ComputationMethods.NancyComputations.CBS import NancyCBS, AvbClass, Rational, Link as NancyLink, \
    Flow as NancyFlow, Plot
from Model import Result
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractNetworkConfiguration import \
    AbstractNetworkConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultEdgeConfiguration import DefaultEdgeConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultFlowConfiguration import DefaultFlowConfiguration
from Model.ComputationConfigurations.Nancy_CBS_Configuration.NancyCBSEdgeConfiguration import NancyCBSEdgeConfiguration
from Model.ComputationConfigurations.Nancy_CBS_Configuration.NancyCBSFlowConfiguration import NancyCBSFlowConfiguration
from Model.Network import Network, Node, Flow, Edge


class NancyCBSNetworkConfiguration(AbstractNetworkConfiguration):

    def __init__(self, max_frame_size_a: int = 64, max_frame_size_b: int = 1522, max_frame_size_nsr: int = 1522,
                 is_strict: bool = False, plot_on_change_in_browser: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.plot_on_change_in_browser: bool = plot_on_change_in_browser
        self.max_frame_size_a: int = max_frame_size_a
        self.max_frame_size_b: int = max_frame_size_b
        self.max_frame_size_nsr: int = max_frame_size_nsr
        self.is_strict: bool = is_strict

    @staticmethod
    def get_configuration_information() -> str:
        return "Nancy: R. Zippo, G. Stea, \"Nancy: an efficient parallel Network Calculus library\",\n" \
               "SoftwareX, Volume 19, July 2022, DOI: 10.1016/j.softx.2022.101178" \
               "\nhttps://rzippo.github.io/nancy/\n\n" \
               "CBS: J. A. R. De Azua and M. Boyer, “Complete modelling of AVB in network calculus framework” in " \
               "Proceedings of the 22nd International Conference on Real-Time Networks and Systems. Versaille, " \
               "France: ACM Press, Oct. 2014, pp. 55–64."

    @staticmethod
    def get_configuration_name() -> str:
        return "Nancy-CBS"

    @staticmethod
    def get_configuration_identifier() -> str:
        return "Nancy-CBS"

    @staticmethod
    def get_edge_configuration_class() -> Type[DefaultEdgeConfiguration]:
        return NancyCBSEdgeConfiguration

    @staticmethod
    def get_flow_configuration_class() -> Type[DefaultFlowConfiguration]:
        return NancyCBSFlowConfiguration

    def to_serializable_dict(self) -> dict:
        own_dict = {"max_frame_size_a": self.max_frame_size_a, "max_frame_size_b": self.max_frame_size_b,
                    "max_frame_size_nsr": self.max_frame_size_nsr, "is_strict": self.is_strict,
                    "plot_on_change_in_browser": self.plot_on_change_in_browser}
        return super().to_serializable_dict() | own_dict

    @staticmethod
    def to_constructor_dict(json_dict: dict, model, network) -> dict:
        own_dict = {"max_frame_size_a": json_dict["max_frame_size_a"],
                    "max_frame_size_b": json_dict["max_frame_size_b"],
                    "max_frame_size_nsr": json_dict["max_frame_size_nsr"], "is_strict": json_dict["is_strict"],
                    "plot_on_change_in_browser": json_dict["plot_on_change_in_browser"]}
        return AbstractNetworkConfiguration.to_constructor_dict(json_dict, model, network) | own_dict

    def make_parameter_dict(self):
        own_dict = {"plot on change in browser": self.plot_on_change_in_browser,
                    "max. frame size A (Byte)": self.max_frame_size_a,
                    "max. frame size B (Byte)": self.max_frame_size_b,
                    "max. frame size NSR (Byte)": self.max_frame_size_nsr, "is strict": self.is_strict}
        return super().make_parameter_dict() | own_dict

    def update_parameter_dict(self, dictionary):
        value = int(dictionary["max. frame size A (Byte)"])
        if value < 0:
            raise ValueError("No negative Frame Size allowed")
        self.max_frame_size_a = value

        value = int(dictionary["max. frame size B (Byte)"])
        if value < 0:
            raise ValueError("No negative Frame Size allowed")
        self.max_frame_size_b = value

        value = int(dictionary["max. frame size NSR (Byte)"])
        if value < 0:
            raise ValueError("No negative Frame Size allowed")
        self.max_frame_size_nsr = value

        true_values = ['true', '1', 't', 'y', 'yes']
        false_values = ['false', '0', 'f', 'n', 'no']
        value = str(dictionary["is strict"]).lower()
        if value in true_values:
            value = True
        elif value in false_values:
            value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.is_strict = value

        value = str(dictionary["plot on change in browser"]).lower()
        if value in true_values:
            value = True
        elif value in false_values:
            value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.plot_on_change_in_browser = value

        return super().update_parameter_dict(dictionary)

    def compute(self, network: Network, result: Result):
        self._compute_args["result"] = result
        self._compute_args["network"] = network
        plt.style.use(["science"])
        plt.rcParams.update({'figure.dpi': '150'})
        _ = scienceplots.inode  # avoid unused import warning
        try:
            result.set_start_time()
            self._make_cbs_object()

            self._compute_end_to_end_delays()
            self._compute_link_delays()
            self._compute_link_backlogs()
            result.set_end_time()

            self._make_plots()
        except Exception as e:
            raise Exception(repr(e))

    def plot_link_curves(self, edge: Edge, run_in_new_process=True):
        """
        Plots curves for a given edge.

        :param edge: edge object
        :param run_in_new_process: whether the plot should be created in a separate process
        """
        if run_in_new_process:
            Process(target=self.plot_link_curves, args=(edge, False)).start()
            return
        self._compute_args["network"] = self.associated_component
        self._make_cbs_object()
        network = self.associated_component
        link_mapping = self._compute_args["link_mapping"]
        nancy_edge_i_j = link_mapping[edge.start, edge.end]
        nancy_edge_j_i = link_mapping[edge.end, edge.start]

        link: NancyLink
        for link in [nancy_edge_i_j, nancy_edge_j_i]:
            curves = []
            names = []
            name_i = network.nodes[UUID(link.NodeI)].name
            name_j = network.nodes[UUID(link.NodeJ)].name

            curves.append(link.ComputeShapingCurve(AvbClass.A))
            names.append(f"Shaper Class A at {name_i}-{name_j}")
            curves.append(link.ComputeShapingCurve(AvbClass.B))
            names.append(f"Shaper Class B at {name_i}-{name_j}")

            curves.append(link.ComputeMinimalServiceCurve(AvbClass.A))
            names.append(f"Min_sc Class A at {name_i}-{name_j}")
            curves.append(link.ComputeMinimalServiceCurve(AvbClass.B))
            names.append(f"Min_sc Class B at {name_i}-{name_j}")

            curves.append(link.ComputeMaximalServiceCurve(AvbClass.A))
            names.append(f"Max_sc Class A at {name_i}-{name_j}")
            curves.append(link.ComputeMaximalServiceCurve(AvbClass.B))
            names.append(f"Max_sc Class B at {name_i}-{name_j}")

            curves.append(link.ComputeIncomingArrivalCurve(AvbClass.A))
            names.append(f"Incoming_ac Class A at {name_i}-{name_j}")
            curves.append(link.ComputeIncomingArrivalCurve(AvbClass.B))
            names.append(f"Incoming_ac Class B at {name_i}-{name_j}")

            curves.append(link.ComputeOutgoingArrivalCurve(AvbClass.A))
            names.append(f"Outgoing_ac Class A at {name_i}-{name_j}")
            curves.append(link.ComputeOutgoingArrivalCurve(AvbClass.B))
            names.append(f"Outgoing_ac Class B at {name_i}-{name_j}")

            Plot.PythonPlot(curves, names)

    def plot_flow_source_ac(self, flow: Flow, run_in_new_process=True):
        """
        Plots curves for a given flow.

        :param flow: flow object
        :param run_in_new_process: whether the plot should be created in a separate process
        """
        if run_in_new_process:
            Process(target=self.plot_flow_source_ac, args=(flow, False)).start()
            return
        self._compute_args["network"] = self.associated_component
        self._make_cbs_object()
        nancy_flow = self._compute_args["flow_mapping"][flow]
        ac = nancy_flow.ComputeSourceAc()
        Plot.PythonPlot(ac, f"Arrival Curve {flow.name}")

    def _make_cbs_object(self):
        """
        Translated the network into a Nancy network.
        """
        network = self._compute_args["network"]
        cbs = NancyCBS(self.max_frame_size_a, self.max_frame_size_b, self.max_frame_size_nsr, self.is_strict)
        self._compute_args["cbs"] = cbs

        link_mapping: dict[tuple[Node, Node], NancyLink] = {}
        self._compute_args["link_mapping"] = link_mapping
        for edge in network.edges.values():
            config: NancyCBSEdgeConfiguration = edge.configurations[self.group_id]
            megabit = 10 ** 6
            link_i_j = NancyLink(cbs, str(edge.id), str(edge.start.id), str(edge.end.id),
                                 int(config.link_speed * megabit), int(config.idle_slope_a * megabit),
                                 int(config.send_slope_a * megabit), int(config.idle_slope_b * megabit),
                                 int(config.send_slope_b * megabit))
            link_j_i = NancyLink(cbs, str(edge.id), str(edge.end.id), str(edge.start.id),
                                 int(config.link_speed * megabit), int(config.idle_slope_a * megabit),
                                 int(config.send_slope_a * megabit), int(config.idle_slope_b * megabit),
                                 int(config.send_slope_b * megabit))
            link_mapping[edge.start, edge.end] = link_i_j
            link_mapping[edge.end, edge.start] = link_j_i

        flow_mapping: dict[Flow, NancyFlow] = {}
        self._compute_args["flow_mapping"] = flow_mapping
        for flow in network.flows.values():
            config: NancyCBSFlowConfiguration = flow.configurations[self.group_id]

            path = []
            for index, node_i in enumerate(flow.path):
                if index + 1 == len(flow.path):
                    break
                node_j = flow.path[index + 1]
                path.append(link_mapping[node_i, node_j])

            if config.avb_class.upper() == "A":
                avb_class = AvbClass.A
            elif config.avb_class.upper() == "B":
                avb_class = AvbClass.B
            else:
                avb_class = AvbClass.Nsr

            cmi = Rational(config.class_measurement_interval.numerator, config.class_measurement_interval.denominator)

            flow_mapping[flow] = NancyFlow(str(flow.id), path, avb_class, config.is_periodic, config.is_worst_case,
                                           config.max_frame_size, cmi, config.max_interval_frame)
        cbs.SetFlows(list(flow_mapping.values()))

    def _get_used_links(self) -> list[NancyLink]:
        flow_mapping = self._compute_args["flow_mapping"]
        used_links = set()
        flow: NancyFlow
        for flow in flow_mapping.values():
            [used_links.add(link) for link in flow.Path]

        network = self._compute_args["network"]
        used_links = sorted(
            used_links,
            key=lambda link: f"{network.nodes[UUID(link.NodeI)].name}-{network.nodes[UUID(link.NodeJ)].name}")
        return used_links

    def _compute_end_to_end_delays(self):
        """
        Computes the end-to-end delays of the current network for the flows of interest.
        """
        result = self._compute_args["result"]
        flow_mapping = self._compute_args["flow_mapping"]
        network = self._compute_args["network"]

        delays_a = []
        delays_b = []
        names_a = []
        names_b = []
        result.append_result("End-to-End Delay:")
        for flow_id in self.flow_ids_of_interest:
            flow = network.flows[flow_id]
            nancy_flow: NancyFlow = flow_mapping[flow]
            delay = Fraction(str(nancy_flow.ComputeEndToEndDelay()))
            result.append_result(f"{flow.name}: ~{delay.__float__()}s ({delay})", 1)
            if nancy_flow.AvbClass == AvbClass.A:
                delays_a.append(delay.__float__())
                names_a.append(flow.name)
            else:
                delays_b.append(delay.__float__())
                names_b.append(flow.name)
        result.append_result("")

        self._compute_args["e2e"] = names_a, delays_a, names_b, delays_b

    def _compute_link_delays(self):
        """
        Computes the delays at every link for class A and B flows.
        """
        result = self._compute_args["result"]
        network: Network = self._compute_args["network"]

        results_a = []
        results_b = []
        names = []
        result_a = ""
        result_b = ""
        for nancy_link in self._get_used_links():
            node_i, node_j = network.nodes[UUID(nancy_link.NodeI)], network.nodes[UUID(nancy_link.NodeJ)]
            link_name = f"{node_i.name}-{node_j.name}"
            delay_a = Fraction(str(nancy_link.ComputeDelay(AvbClass.A)))
            result_a += f"{link_name}: ~{delay_a.__float__()}s ({delay_a})\n"
            delay_b = Fraction(str(nancy_link.ComputeDelay(AvbClass.B)))
            result_b += f"{link_name}: ~{delay_b.__float__()}s ({delay_b})\n"

            names.append(link_name)
            results_a.append(delay_a)
            results_b.append(delay_b)

        result.append_result("Link delay for class A:")
        result.append_result(result_a, 1)
        result.append_result("Link delay for class B:")
        result.append_result(result_b, 1)

        self._compute_args["delay_link"] = names, results_a, results_b

    def _compute_link_backlogs(self):
        """
        Computes backlog bounds at links of class A and B flows.
        """
        result = self._compute_args["result"]
        network: Network = self._compute_args["network"]

        results_a = []
        results_b = []
        names = []
        result_a = ""
        result_b = ""
        for nancy_link in self._get_used_links():
            node_i, node_j = network.nodes[UUID(nancy_link.NodeI)], network.nodes[UUID(nancy_link.NodeJ)]
            link_name = f"{node_i.name}-{node_j.name}"
            backlog_a = Fraction(str(nancy_link.ComputeBacklog(AvbClass.A)))
            result_a += f"{link_name}: ~{backlog_a.__float__()} bit ({backlog_a})\n"
            backlog_b = Fraction(str(nancy_link.ComputeBacklog(AvbClass.B)))
            result_b += f"{link_name}: ~{backlog_b.__float__()} bit ({backlog_b})\n"

            names.append(link_name)
            results_a.append(backlog_a)
            results_b.append(backlog_b)

        result.append_result("Link backlog for class A:")
        result.append_result(result_a, 1)
        result.append_result("Link backlog for class B:")
        result.append_result(result_b, 1)

        self._compute_args["backlog_link"] = names, results_a, results_b

    def _make_plots(self):
        """
        Creates plots of the results.
        """
        names_a, results_a, names_b, results_b = self._compute_args["e2e"]
        if len(names_a) + len(names_b) < 50:
            self._bar_chart(names_a, results_a, names_b, results_b, x_label="Flows", y_label="End-to-End Delay (s)",
                            display_name="End-to-End Delay")
        self._boxplot(results_a, results_b, x_label="Flows", y_label="End-to-End Delay (s)",
                      display_name="Aggregated Delays")

        names, results_a, results_b = self._compute_args["delay_link"]
        if len(names) < 50:
            self._bar_chart(names, results_a, names, results_b, display_name="Link Delay", x_label="Edges",
                            y_label="Delay (s)", is_equal_names=True)
        self._boxplot(results_a, results_b, x_label="Edges", y_label="Delay (s)",
                      display_name="Aggregated Link Delays")

        names, results_a, results_b = self._compute_args["backlog_link"]
        if len(names) < 50:
            self._bar_chart(names, results_a, names, results_b, display_name="Backlog", x_label="Edges",
                            y_label="Backlog (bit)", is_equal_names=True)
        self._boxplot(results_a, results_b, x_label="Edges", y_label="Backlog (bit)",
                      display_name="Aggregated Backlogs")

    def _bar_chart(self, names_a, values_a, names_b, values_b, x_label, y_label, label_a="Class A",
                   label_b="Class B", display_name="Plot", is_equal_names=False):
        fig = plt.figure()
        axe = fig.add_subplot(111)

        if is_equal_names:
            x_index = np.arange(len(names_a))
            axe.bar(x_index - 0.2, values_a, 0.4, label=label_a)
            axe.bar(x_index + 0.2, values_b, 0.4, label=label_b)
            axe.set_xticks(ticks=x_index)
            axe.set_xticklabels(names_a)
        else:
            axe.bar(names_a, values_a, label=label_a)
            axe.bar(names_b, values_b, label=label_b)

        axe.set_xlabel(x_label)
        axe.set_ylabel(y_label)
        axe.legend()

        result = self._compute_args["result"]
        result.add_plot(fig, display_name)

    def _boxplot(self, values_a, values_b, x_label, y_label, label_a="Class A",
                 label_b="Class B", display_name="Plot"):
        """
        Creates a boxplot for the given values.

        :param values_a: values of group A
        :param values_b: values of group B
        :param x_label: x label
        :param y_label: y label
        :param label_a: a label for group A
        :param label_b: a label for group B
        :param display_name: name of the plot
        """
        fig = plt.figure()
        axe = fig.add_subplot(111)
        data = [values_a, values_b]
        labels = [label_a, label_b]
        axe.boxplot(data, labels=labels)
        axe.set_xlabel(x_label)
        axe.set_ylabel(y_label)

        result = self._compute_args["result"]
        result.add_plot(fig, display_name)
