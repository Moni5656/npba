import tkinter

from Model.Network.Edge import Edge
from Model.Network.Node import Node
from View.GUI.Windows.GraphWindow.GraphCanvas import GraphCanvas
from View.Observer import Observer
from utils.utils import OS


class EdgeView(Observer):
    start_node = None
    EDGE_THICKNESS = 3
    EDGE_HIGHLIGHT_THICKNESS = 4

    def __init__(self, canvas: GraphCanvas, edge: Edge):
        self.canvas = canvas
        self.button_bar = canvas.button_bar
        self.controller = canvas.controller
        self.canvas_line = None
        super().__init__(edge)

        self.draw_edge()
        edge.start.subscribe(self)
        edge.end.subscribe(self)

    def draw_edge(self) -> None:
        """
        Draws an edge or deletes and redraws the current edge when the x/y coordinates of a node change.
        """
        if self.canvas_line is not None:
            self.canvas.delete(self.canvas_line)
        start_node_x, start_node_y = self.canvas.coords_model_to_canvas(self.observed_subject.start.x,
                                                                        self.observed_subject.start.y)
        end_node_x, end_node_y = self.canvas.coords_model_to_canvas(self.observed_subject.end.x,
                                                                    self.observed_subject.end.y)
        self.canvas_line = self.canvas.draw_advanced_line(start_node_x, start_node_y, end_node_x, end_node_y, r=-1,
                                                          is_curved=False,
                                                          shorten_start=51 * self.canvas.scale_factor,
                                                          shorten_end=51 * self.canvas.scale_factor, arrow=tkinter.BOTH,
                                                          arrowshape=(
                                                              8 * self.canvas.scale_factor,
                                                              10 * self.canvas.scale_factor,
                                                              3 * self.canvas.scale_factor),
                                                          width=self.canvas.scale_factor * EdgeView.EDGE_THICKNESS,
                                                          tags="edge")
        self.set_edge_activity()
        self.canvas.lower(self.canvas_line)
        self.bind_edge()

    def bind_edge(self) -> None:
        """
        Creates all edge bindings.
        """
        self.canvas.tag_bind(self.canvas_line, OS.left_mouse_button, self.on_left_click)
        self.canvas.tag_bind(self.canvas_line, OS.shift_left_mouse_button, self.on_shift_left_click)

    def set_edge_activity(self) -> None:
        """
        Changes the color of the edge according to the current activity.
        """
        if self.observed_subject.is_selected:
            self.canvas.itemconfigure(self.canvas_line, fill="black",
                                      width=EdgeView.EDGE_HIGHLIGHT_THICKNESS * self.canvas.scale_factor)
            self.canvas.lift(self.canvas_line)
        else:
            self.canvas.itemconfigure(self.canvas_line, fill="#666666",
                                      width=EdgeView.EDGE_THICKNESS * self.canvas.scale_factor)

    def destroy(self) -> None:
        """
        Removes the edge from the canvas.
        """
        self.canvas.delete(self.canvas_line)
        self.observed_subject: Edge
        self.observed_subject.end.unsubscribe(self)
        self.observed_subject.start.unsubscribe(self)
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None

    def on_left_click(self, _) -> None:
        """
        Handles left click events.

        :param _: click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.flow_button_pressed:
            return
        if self.button_bar.delete_button_pressed:
            self.controller.delete_component(self.observed_subject)
            return
        self.controller.on_component_click(self.observed_subject)

    def on_shift_left_click(self, _) -> None:
        """
        Handles Shift+Left click events.
        :param _: Shift+Left click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.delete_button_pressed or self.button_bar.flow_button_pressed:
            return
        self.controller.on_component_shift_click(self.observed_subject)

    def update_(self, updated_component) -> None:
        """
         Triggered when the observed edge or nodes are updated in the model. Handles any resulting changes.

         :param updated_component: information about the updated nodes or edge
         """
        if isinstance(updated_component[0], Node):
            if updated_component[1] == "set_parameter":
                self.draw_edge()
        if isinstance(updated_component[0], Edge):
            if updated_component[1] == "set_selection":
                self.set_edge_activity()

    @staticmethod
    def follow_mouse_cursor(canvas: GraphCanvas, event):
        """
        Preview of adding a new edge.

        :param canvas: canvas object
        :param event: mouse event
        """
        x, y = canvas.coords_event_to_canvas(event)
        x_start, y_start = canvas.coords_model_to_canvas(EdgeView.start_node.x, EdgeView.start_node.y)
        canvas.delete("preview")
        preview_edge = canvas.draw_advanced_line(x_start, y_start, x, y, r=-1, is_curved=False, arrow=tkinter.BOTH,
                                                 arrowshape=(
                                                     8 * canvas.scale_factor, 10 * canvas.scale_factor,
                                                     3 * canvas.scale_factor),
                                                 width=EdgeView.EDGE_THICKNESS * canvas.scale_factor, tags="preview")
        canvas.lower(preview_edge)
