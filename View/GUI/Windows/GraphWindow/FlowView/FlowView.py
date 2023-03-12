import tkinter

from Model.Network.Flow import Flow
from View.GUI.Windows.GraphWindow.FlowView.FlowPartView import FlowPartView
from View.GUI.Windows.GraphWindow.GraphCanvas import GraphCanvas
from View.Observer import Observer


class FlowView(Observer):
    start_node = None
    current_flow = None

    def __init__(self, canvas: GraphCanvas, flow: Flow):
        super().__init__(flow)
        self.canvas = canvas
        self.button_bar = canvas.button_bar
        self.controller = canvas.controller
        self.flow_part_manager = {}

        self.initialize_flow_part_manager()
        self.initial_draw()

    def initialize_flow_part_manager(self):
        """
        Initializes a flow part manager for the flow.
        """
        from View.GUI.Windows.GraphWindow.FlowView.FlowPartManager import FlowPartManager

        for index in range(len(self.observed_subject.path) - 1):
            start = self.observed_subject.path[index]
            end = self.observed_subject.path[index + 1]

            if (self.canvas, start, end) in FlowPartManager.active_flow_manager:
                manager = FlowPartManager.active_flow_manager[(self.canvas, start, end)]
            else:
                manager = FlowPartManager(self.canvas, start, end)

            self.flow_part_manager[(start, end)] = manager

    def update_(self, updated_component):
        if isinstance(updated_component[0], Flow):
            if updated_component[1] == "set_selection":
                self.reconfigure()
            if updated_component[1] == "update_path":
                for manager in self.flow_part_manager.values():
                    manager.remove_flow(self.observed_subject)
                self.flow_part_manager.clear()
                self.initialize_flow_part_manager()
                self.initial_draw()
            if updated_component[1] == "set_parameter":
                self.reconfigure()

    def destroy(self) -> None:
        """
        Removes the flow from the canvas.
        """
        for manager in self.flow_part_manager.values():
            manager.remove_flow(self.observed_subject)
        self.flow_part_manager = {}
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None

    def initial_draw(self):
        """
        Adds the flow to each flow part manager.
        """
        for manager in self.flow_part_manager.values():
            manager.add_flow(self.observed_subject)

    def redraw(self):
        """
        Redraws the flow in each flow part manager.
        """
        for manager in self.flow_part_manager.values():
            manager.redraw_flow(self.observed_subject)

    def reconfigure(self):
        """
        Reconfigures the flow in each flow part manager.
        """
        for manager in self.flow_part_manager.values():
            manager.reconfigure_flow(self.observed_subject)

    @staticmethod
    def follow_mouse_cursor(canvas: GraphCanvas, event):
        """
        Creates a preview when adding new flow parts.

        :param canvas: canvas object
        :param event: mouse event
        """
        x, y = canvas.coords_event_to_canvas(event)
        x_start, y_start = canvas.coords_model_to_canvas(FlowView.start_node.x, FlowView.start_node.y)
        canvas.delete("preview")
        preview_flow = canvas.draw_advanced_line(x_start, y_start, x, y, r=4, arrow=tkinter.LAST,
                                                 arrowshape=(
                                                     8 * canvas.scale_factor, 10 * canvas.scale_factor,
                                                     3 * canvas.scale_factor),
                                                 width=FlowPartView.FLOW_THICKNESS * canvas.scale_factor,
                                                 tags="preview")
        canvas.lower(preview_flow)
