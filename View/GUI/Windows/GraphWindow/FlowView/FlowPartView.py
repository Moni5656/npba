import tkinter as tk

from Model.Network.Flow import Flow
from Model.Network.Node import Node
from View.GUI.Windows.GraphWindow.GraphCanvas import GraphCanvas
from utils.utils import OS


class FlowPartView:
    FLOW_THICKNESS = 3
    FLOW_HIGHLIGHT_THICKNESS = 4

    def __init__(self, canvas: GraphCanvas, flow: Flow, start: Node, end: Node, radius):
        self.canvas = canvas
        self.flow = flow
        self.button_bar = self.canvas.button_bar
        self.controller = self.canvas.controller
        self.canvas_line = None
        self.start_node = start
        self.end_node = end
        self.radius = radius
        self.draw_flow()

    def draw_flow(self) -> None:
        """
        Draws a flow or deletes and redraws the current flow when the x/y coordinates of a node change.
        """
        if self.canvas_line is not None:
            self.canvas.delete(self.canvas_line)
        r = self.radius
        start_node_x, start_node_y = self.canvas.coords_model_to_canvas(self.start_node.x, self.start_node.y)
        end_node_x, end_node_y = self.canvas.coords_model_to_canvas(self.end_node.x, self.end_node.y)
        self.canvas_line = self.canvas.draw_advanced_line(start_node_x, start_node_y, end_node_x, end_node_y,
                                                          r=r,
                                                          shorten_start=51 * self.canvas.scale_factor,
                                                          shorten_end=51 * self.canvas.scale_factor, arrow=tk.LAST,
                                                          arrowshape=(
                                                              8 * self.canvas.scale_factor,
                                                              10 * self.canvas.scale_factor,
                                                              3 * self.canvas.scale_factor),
                                                          width=self.canvas.scale_factor * FlowPartView.FLOW_THICKNESS,
                                                          tags="flow")
        self.configure_line()
        self.bind_flow()

    def bind_flow(self) -> None:
        """
        Creates all flow bindings.
        """
        self.canvas.tag_bind(self.canvas_line, OS.left_mouse_button, self.on_left_click)
        self.canvas.tag_bind(self.canvas_line, OS.shift_left_mouse_button, self.on_shift_left_click)

    def delete_from_canvas(self) -> None:
        """
        Removes the flow from the canvas.
        """
        self.canvas.delete(self.canvas_line)

    def configure_line(self) -> None:
        """
        Changes the color of the flow part according to the current flow activity.
        """
        if self.flow.is_selected:
            self.canvas.itemconfigure(self.canvas_line, fill=self.flow.highlight_color,
                                      width=FlowPartView.FLOW_HIGHLIGHT_THICKNESS * self.canvas.scale_factor,
                                      dash=())
            self.canvas.lift(self.canvas_line)

        else:
            self.canvas.itemconfigure(self.canvas_line, fill=self.flow.color,
                                      width=FlowPartView.FLOW_THICKNESS * self.canvas.scale_factor,
                                      dash=(8, 8))

    def on_left_click(self, _) -> None:
        """
        Handles left click events.

        :param _: click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.flow_button_pressed:
            return
        if self.button_bar.delete_button_pressed:
            self.controller.delete_component(self.flow)
            return
        self.controller.on_component_click(self.flow)

    def on_shift_left_click(self, _) -> None:
        """
        Handles Shift+Left click events.

        :param _: Shift+Left click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.delete_button_pressed or self.button_bar.flow_button_pressed:
            return
        self.controller.on_component_shift_click(self.flow)
