import tkinter as tk

from Model.Network.Flow import Flow
from Model.Network.Node import Node
from View.GUI.Windows.GraphWindow.GraphCanvas import GraphCanvas
from utils.utils import OS


class GroupedFlowPartView:
    FLOW_HIGHLIGHT_THICKNESS = 4
    FLOW_THICKNESS = 3

    def __init__(self, canvas: GraphCanvas, start: Node, end: Node, radius):
        self.canvas = canvas
        self.managed_flows = []
        self.button_bar = self.canvas.button_bar
        self.controller = self.canvas.controller
        self.canvas_line = None
        self.start_node = start
        self.end_node = end
        self.radius = radius

    def add(self, flow: Flow):
        """
        Adds a flow to the group.

        :param flow: flow object
        """
        self.managed_flows.append(flow)
        self.draw_flow()

    def remove(self, flow: Flow):
        """
        Removes a flow from the group.

        :param flow: flow object
        """
        self.managed_flows.remove(flow)
        if len(self.managed_flows) == 0:
            self.draw_flow()

    def remove_first(self):
        """
        Removes and returns the first flow of the group.

        :return: removed flow object
        """
        flow = self.managed_flows[0]
        self.remove(flow)
        return flow

    def draw_flow(self) -> None:
        """
        Draws a flow or deletes and redraws the current flow when the x/y coordinates of a node change.
        """
        if self.canvas_line is not None:
            self.canvas.delete(self.canvas_line)
        if len(self.managed_flows) == 0:
            return

        start_node_x, start_node_y = self.canvas.coords_model_to_canvas(self.start_node.x, self.start_node.y)
        end_node_x, end_node_y = self.canvas.coords_model_to_canvas(self.end_node.x, self.end_node.y)
        self.canvas_line = self.canvas.draw_advanced_line(
            start_node_x, start_node_y, end_node_x, end_node_y, r=self.radius,
            shorten_start=51 * self.canvas.scale_factor, shorten_end=51 * self.canvas.scale_factor, arrow=tk.LAST,
            arrowshape=(8 * self.canvas.scale_factor, 10 * self.canvas.scale_factor, 3 * self.canvas.scale_factor),
            width=self.canvas.scale_factor * GroupedFlowPartView.FLOW_THICKNESS, tags="grouped_flow")
        self.configure_line()
        self.bind_flow()

    def configure_line(self) -> None:
        """
        Changes the color of the flow part according to the current flow activity.
        """
        is_selected = any(map(lambda flow: flow.is_selected, self.managed_flows))
        if is_selected:
            self.canvas.itemconfigure(self.canvas_line,
                                      width=GroupedFlowPartView.FLOW_HIGHLIGHT_THICKNESS * self.canvas.scale_factor,
                                      dash=())
            self.canvas.lift(self.canvas_line)
        else:
            self.canvas.itemconfigure(self.canvas_line,
                                      width=GroupedFlowPartView.FLOW_THICKNESS * self.canvas.scale_factor,
                                      dash=(8, 8))

    def bind_flow(self) -> None:
        """
        Creates all flow bindings.
        """
        self.canvas.tag_bind(self.canvas_line, OS.left_mouse_button, self.on_left_click)
        self.canvas.tag_bind(self.canvas_line, OS.shift_left_mouse_button, self.on_shift_left_click)

    def on_left_click(self, _) -> None:
        """
        Handles left click events.

        :param _: click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.flow_button_pressed:
            return
        if self.button_bar.delete_button_pressed:
            return
        self.controller.model_facade.unselect_all_components()
        for flow in self.managed_flows:
            self.controller.on_component_shift_click(flow)

    def on_shift_left_click(self, _) -> None:
        """
        Handles Shift+Left click events.

        :param _: Shift+Left click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.delete_button_pressed or self.button_bar.flow_button_pressed:
            return
        for flow in self.managed_flows:
            self.controller.on_component_shift_click(flow)
