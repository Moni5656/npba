import pathlib
import shutil
import tempfile
from typing import Type

import numpy as np
import scienceplots
from matplotlib import pyplot as plt

from ComputationMethods.RTCToolboxCBS.MatlabWrapper import MatlabWrapper
from Model import Result
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractNetworkConfiguration import \
    AbstractNetworkConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultEdgeConfiguration import DefaultEdgeConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultFlowConfiguration import DefaultFlowConfiguration
from Model.ComputationConfigurations.RTCToolbox_CBS_Configuration.RTCToolboxCBSEdgeConfiguration import \
    RTCToolboxCBSEdgeConfiguration
from Model.ComputationConfigurations.RTCToolbox_CBS_Configuration.RTCToolboxCBSFlowConfiguration import \
    RTCToolboxCBSFlowConfiguration
from Model.Network import Network


class RTCToolboxCBSNetworkConfiguration(AbstractNetworkConfiguration):

    def __init__(self, max_frame_size_a: int = 64, max_frame_size_b: int = 1522, max_frame_size_nsr: int = 1522,
                 is_strict: bool = False, save_matlab_plots=False, **kwargs):
        super().__init__(**kwargs)
        self.max_frame_size_a: int = max_frame_size_a
        self.max_frame_size_b: int = max_frame_size_b
        self.max_frame_size_nsr: int = max_frame_size_nsr
        self.is_strict: bool = is_strict

        self.save_matlab_plots = save_matlab_plots

    @staticmethod
    def get_configuration_information() -> str:
        return "RTCToolbox: Wandeler, Ernesto. Modular performance analysis and interface-based design for embedded" \
               " real-time systems. Shaker, 2006.\n" \
               "https://www.mpa.ethz.ch/#mozTocId588080\n\n" \
               "CBS: J. A. R. De Azua and M. Boyer, “Complete modelling of AVB in network calculus framework” in " \
               "Proceedings of the 22nd International Conference on Real-Time Networks and Systems. Versaille, " \
               "France: ACM Press, Oct. 2014, pp. 55–64."

    @staticmethod
    def get_configuration_name() -> str:
        return "RTCToolbox-CBS"

    @staticmethod
    def get_configuration_identifier() -> str:
        return "rtctoolbox-matlab-CBS"

    @staticmethod
    def get_edge_configuration_class() -> Type[DefaultEdgeConfiguration]:
        return RTCToolboxCBSEdgeConfiguration

    @staticmethod
    def get_flow_configuration_class() -> Type[DefaultFlowConfiguration]:
        return RTCToolboxCBSFlowConfiguration

    def to_serializable_dict(self) -> dict:
        own_dict = {"save_matlab_plots": self.save_matlab_plots, "max_frame_size_a": self.max_frame_size_a,
                    "max_frame_size_b": self.max_frame_size_b, "max_frame_size_nsr": self.max_frame_size_nsr,
                    "is_strict": self.is_strict}
        return super().to_serializable_dict() | own_dict

    @staticmethod
    def to_constructor_dict(json_dict: dict, model, network) -> dict:
        own_dict = {"save_matlab_plots": json_dict["save_matlab_plots"],
                    "max_frame_size_a": json_dict["max_frame_size_a"],
                    "max_frame_size_b": json_dict["max_frame_size_b"],
                    "max_frame_size_nsr": json_dict["max_frame_size_nsr"], "is_strict": json_dict["is_strict"]}
        return AbstractNetworkConfiguration.to_constructor_dict(json_dict, model, network) | own_dict

    def make_parameter_dict(self):
        own_dict = {"save matlab plots": self.save_matlab_plots, "max. frame size A (Byte)": self.max_frame_size_a,
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

        value = str(dictionary["save matlab plots"]).lower()
        if value in true_values:
            value = True
        elif value in false_values:
            value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.save_matlab_plots = value

        return super().update_parameter_dict(dictionary)

    def compute(self, network: Network, result: Result):
        plt.style.use(["science"])
        plt.rcParams.update({'figure.dpi': '150'})
        _ = scienceplots.inode  # avoid unused import warning

        self._compute_args["matlab"] = matlab = MatlabWrapper()
        self._compute_args["result"] = result
        self._compute_args["network"] = network
        self._compute_args["tmp_dir"] = tempfile.gettempdir()
        tmp_dir_path = pathlib.Path(tempfile.gettempdir()).joinpath(str(result.id))
        tmp_dir_path.mkdir()

        matlab._get_engine()
        result.set_start_time()
        self._make_matlab_objects()
        self._compute_end_to_end_delays()
        self._compute_link_delays()
        self._compute_link_backlogs()
        result.set_end_time()
        self._make_plots()

        if self.save_matlab_plots:
            result.append_result(f"\nCurve plots are saved at:\n{tmp_dir_path}\n")
        else:
            shutil.rmtree(tmp_dir_path, ignore_errors=True)
        matlab.exit()

    def _make_matlab_objects(self):
        """
        Translates the current network into a MATLAB network.
        """
        matlab: MatlabWrapper = self._compute_args["matlab"]
        self._compute_args["link_mapping"] = link_mapping = {}
        megabit = 10 ** 6
        for edge in self.associated_component.edges.values():
            configuration: RTCToolboxCBSEdgeConfiguration = edge.configurations[self.group_id]
            link_mapping[edge.start, edge.end] = matlab.Link(
                f"{edge.start.name}-{edge.end.name}", edge.start.name, edge.end.name,
                configuration.link_speed * megabit, configuration.idle_slope_a * megabit,
                configuration.send_slope_a * megabit, configuration.idle_slope_b * megabit,
                configuration.send_slope_b * megabit)
            link_mapping[edge.end, edge.start] = matlab.Link(
                f"{edge.end.name}-{edge.start.name}", edge.end.name, edge.start.name,
                configuration.link_speed * megabit, configuration.idle_slope_a * megabit,
                configuration.send_slope_a * megabit, configuration.idle_slope_b * megabit,
                configuration.send_slope_b * megabit)

        self._compute_args["flow_mapping"] = flow_mapping = {}
        for flow in self.associated_component.flows.values():
            path = []
            for index, node_i in enumerate(flow.path):
                if index + 1 == len(flow.path):
                    break
                node_j = flow.path[index + 1]
                path.append(link_mapping[node_i, node_j])
            configuration: RTCToolboxCBSFlowConfiguration = flow.configurations[self.group_id]
            flow_mapping[flow] = matlab.Flow(
                flow.name, configuration.max_frame_size, configuration.class_measurement_interval,
                configuration.max_interval_frame, path, configuration.avb_class,
                "p" if configuration.is_periodic else "np", "wc" if configuration.is_worst_case else "nwc")

        m_flows = list(flow_mapping.values())
        self._compute_args["cbs"] = matlab.CBS(
            self.max_frame_size_a, self.max_frame_size_b, self.max_frame_size_nsr, self.is_strict, m_flows)

    def _compute_end_to_end_delays(self):
        """
        Computes the end-to-end delays for every flow of interest.
        """
        result = self._compute_args["result"]
        result.append_result("End-to-End Delay:")
        tmp_dir = self._compute_args["tmp_dir"]
        network = self._compute_args["network"]
        matlab: MatlabWrapper = self._compute_args["matlab"]
        flow_mapping = self._compute_args["flow_mapping"]
        cbs = self._compute_args["cbs"]

        delays_a = []
        names_a = []
        delays_b = []
        names_b = []
        for flow_id in self.flow_ids_of_interest:
            flow = network.flows[flow_id]
            m_flow = flow_mapping[flow]
            delay = matlab.end_to_end_delay(cbs, m_flow, tmp_dir, str(result.id))
            result.append_result(f"{flow.name}: {delay}s", 1)

            if flow.configurations[self.group_id].avb_class == "A":
                delays_a.append(delay)
                names_a.append(flow.name)
            else:
                delays_b.append(delay)
                names_b.append(flow.name)
        result.append_result("")

        self._compute_args["e2e"] = names_a, delays_a, names_b, delays_b

    def _compute_link_delays(self):
        """
        Computes the delay at links of class A and B flows.
        """
        result = self._compute_args["result"]
        tmp_dir = self._compute_args["tmp_dir"]
        cbs = self._compute_args["cbs"]
        matlab: MatlabWrapper = self._compute_args["matlab"]
        link_mapping = self._compute_args["link_mapping"]

        results_a = []
        results_b = []
        names = []
        result_a = ""
        result_b = ""
        for (node_i, node_j) in self._get_used_links():
            link = link_mapping[node_i, node_j]
            link_name = f"{node_i.name}-{node_j.name}"
            delay_a = matlab.delay_link(cbs, link, "A", tmp_dir, str(result.id))
            result_a += f"{link_name}: {delay_a}s\n"
            delay_b = matlab.delay_link(cbs, link, "B", tmp_dir, str(result.id))
            result_b += f"{link_name}: {delay_b}s\n"

            names.append(link_name)
            results_a.append(delay_a)
            results_b.append(delay_b)

        result.append_result("Link delay for class A:")
        result.append_result(result_a, 1)
        result.append_result("Link delay for class B:")
        result.append_result(result_b, 1)

        self._compute_args["link_delay"] = names, results_a, results_b

    def _compute_link_backlogs(self):
        """
        Computes backlog bounds of links of class A and B flows.
        """
        result = self._compute_args["result"]
        tmp_dir = self._compute_args["tmp_dir"]
        cbs = self._compute_args["cbs"]
        matlab: MatlabWrapper = self._compute_args["matlab"]
        link_mapping = self._compute_args["link_mapping"]

        results_a = []
        results_b = []
        names = []
        result_a = ""
        result_b = ""
        for (node_i, node_j) in self._get_used_links():
            link = link_mapping[node_i, node_j]
            link_name = f"{node_i.name}-{node_j.name}"
            backlog_a = matlab.backlog_link(cbs, link, "A", tmp_dir, str(result.id))
            result_a += f"{link_name}: {backlog_a} bit\n"
            backlog_b = matlab.backlog_link(cbs, link, "B", tmp_dir, str(result.id))
            result_b += f"{link_name}: {backlog_b} bit\n"

            names.append(link_name)
            results_a.append(backlog_a)
            results_b.append(backlog_b)

        result.append_result("Link backlog for class A:")
        result.append_result(result_a, 1)
        result.append_result("Link backlog for class B:")
        result.append_result(result_b, 1)

        self._compute_args["link_backlog"] = names, results_a, results_b

    def _get_used_links(self):
        """
        Returns a list of used links.

        :return: sorted list of used links
        """
        network = self._compute_args["network"]
        used_links = set()
        for flow in network.flows.values():
            for index, node_i in enumerate(flow.path):
                if index + 1 == len(flow.path):
                    break
                node_j = flow.path[index + 1]
                used_links.add((node_i, node_j))
        used_links = sorted(used_links, key=lambda t: f"{t[0].name}-{t[1].name}")
        return used_links

    def _make_plots(self):
        """
        Creates plots for the computed results.
        """
        names_a, results_a, names_b, results_b = self._compute_args["e2e"]
        if len(names_a) + len(names_b) < 50:
            self._bar_chart(names_a, results_a, names_b, results_b, x_label="Flows", y_label="End-to-End Delay (s)",
                            display_name="End-to-End Delay")
        self._boxplot(results_a, results_b, x_label="Flows", y_label="End-to-End Delay (s)",
                      display_name="Aggregated Delays")

        names, results_a, results_b = self._compute_args["link_delay"]
        if len(names) < 50:
            self._bar_chart(names, results_a, names, results_b, x_label="Edges", y_label="Delay (s)",
                            display_name="Link Delay")
        self._boxplot(results_a, results_b, x_label="Edges", y_label="Delay (s)",
                      display_name="Aggregated Link Delays")

        names, results_a, results_b = self._compute_args["link_backlog"]
        if len(names) < 50:
            self._bar_chart(names, results_a, names, results_b, x_label="Edges", y_label="Backlog (bit)",
                            display_name="Backlog")
        self._boxplot(results_a, results_b, x_label="Edges", y_label="Backlog (bit)",
                      display_name="Aggregated Backlogs")

    def _bar_chart(self, names_a, values_a, names_b, values_b, x_label, y_label, label_a="Class A", label_b="Class B",
                   display_name="Plot"):
        """
        Creates a bar chart for the computed results.

        :param names_a: names of values of a group A
        :param values_a: values of a group A
        :param names_b: names of values of a group B
        :param values_b: values of a group B
        :param x_label: x label
        :param y_label: y label
        :param label_a: label for group A
        :param label_b: label for group B
        :param display_name: name of the plot
        """
        fig = plt.figure()
        axe = fig.add_subplot(111)
        is_equal_names = names_a == names_b

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
        Creates a boxplot for the computed results.

        :param values_a: values of a group A
        :param values_b: values of a group B
        :param x_label: x label
        :param y_label: y label
        :param label_a: label for group A
        :param label_b: label for group B
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
