from Model.Network.Edge import Edge
from Model.Network.Flow import Flow
from Model.Network.Node import Node
from View.GUI.CustomWidgets.ScrolledFrame import ScrolledFrame
from View.GUI.Windows import WindowInterface, Position
from View.GUI.Windows.ParameterWindow.ComponentSections.EdgeParameterSection import EdgeParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.FlowParameterSection import FlowParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.NetworkParameterSection import NetworkParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.NodeParameterSection import NodeParameterSection
from View.Observer import Observer


class ParameterWindow(WindowInterface, ScrolledFrame, Observer):

    @staticmethod
    def get_title() -> str:
        return "Parameter"

    @staticmethod
    def get_start_position() -> Position:
        return Position.TopRight

    @staticmethod
    def get_importance():
        return 5

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        ScrolledFrame.__init__(self, parent)

        self.observed_subject = network
        self.network_parameter_section = None
        self.node_parameter_sections = {}
        self.edge_parameter_sections = {}
        self.flow_parameter_sections = {}
        self.add_parameter_section()
        Observer.__init__(self, network)

    def add_parameter_section(self):
        """
        Adds a parameter section with entries for existing components.
        """
        self.network_parameter_section = NetworkParameterSection(self.scrolled_frame, self.controller,
                                                                 self.observed_subject)
        for node_id in self.observed_subject.nodes:
            node = self.observed_subject.nodes[node_id]
            node_parameter_section = NodeParameterSection(self.scrolled_frame, node, self.controller)
            self.node_parameter_sections[node] = node_parameter_section
        for edge_id in self.observed_subject.edges:
            edge = self.observed_subject.edges[edge_id]
            edge_parameter_section = EdgeParameterSection(self.scrolled_frame, edge, self.controller)
            self.edge_parameter_sections[edge] = edge_parameter_section
        for flow_id in self.observed_subject.flows:
            flow = self.observed_subject.flows[flow_id]
            flow_parameter_section = FlowParameterSection(self.scrolled_frame, flow, self.controller)
            self.flow_parameter_sections[flow] = flow_parameter_section

    def update_(self, updated_component):
        if isinstance(updated_component[0], Node):
            if updated_component[1] == "add_node":
                node_parameter_section = NodeParameterSection(self.scrolled_frame, updated_component[0],
                                                              self.controller)
                self.node_parameter_sections[updated_component[0]] = node_parameter_section
            elif updated_component[1] == "delete_node":
                self.node_parameter_sections[updated_component[0]].destroy()
                del self.node_parameter_sections[updated_component[0]]
        elif isinstance(updated_component[0], Edge):
            if updated_component[1] == "add_edge":
                edge_parameter_section = EdgeParameterSection(self.scrolled_frame, updated_component[0],
                                                              self.controller)
                self.edge_parameter_sections[updated_component[0]] = edge_parameter_section
            elif updated_component[1] == "delete_edge":
                self.edge_parameter_sections[updated_component[0]].destroy()
                del self.edge_parameter_sections[updated_component[0]]
        elif isinstance(updated_component[0], Flow):
            if updated_component[1] == "add_flow":
                flow_parameter_section = FlowParameterSection(self.scrolled_frame, updated_component[0],
                                                              self.controller)
                self.flow_parameter_sections[updated_component[0]] = flow_parameter_section
            elif updated_component[1] == "delete_flow":
                self.flow_parameter_sections[updated_component[0]].destroy()
                del self.flow_parameter_sections[updated_component[0]]

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        self.network_parameter_section.destroy()
        for node in self.node_parameter_sections:
            self.node_parameter_sections[node].destroy()
        self.node_parameter_sections = {}
        for edge in self.edge_parameter_sections:
            self.edge_parameter_sections[edge].destroy()
        self.edge_parameter_sections = {}
        for flow in self.flow_parameter_sections:
            self.flow_parameter_sections[flow].destroy()
        self.flow_parameter_sections = {}

        super().destroy()
