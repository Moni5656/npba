from Controller.GUI.GUIController import GUIController
from Model.Network import Node
from View.Observer import Observer
from utils.utils import OS


class NodeView(Observer):
    NODE_RADIUS = 50

    def __init__(self, observed_subject: Node, button_bar, graph_canvas):
        super().__init__(observed_subject)
        self.x = observed_subject.x
        self.y = observed_subject.y
        self.button_bar = button_bar
        self.canvas = graph_canvas
        self.controller: GUIController = graph_canvas.controller

        self.circle = None
        self.text = None
        self.is_selected = observed_subject.is_selected
        self.draw_node()
        self.bind_node()

    def update_(self, updated_component):
        """
        Triggered when the observed node is updated in the model. Handles any resulting changes.
        :param updated_component: information about the updated node
        """
        old_x, old_y = self.canvas.coords_model_to_canvas(self.x, self.y)
        new_x, new_y = self.canvas.coords_model_to_canvas(self.observed_subject.x, self.observed_subject.y)
        diff_x, diff_y = new_x - old_x, new_y - old_y
        self.canvas.move(self.circle, diff_x, diff_y)
        self.canvas.move(self.text, diff_x, diff_y)

        self.x = self.observed_subject.x
        self.y = self.observed_subject.y
        self.is_selected = self.observed_subject.is_selected
        if self.observed_subject.is_selected:
            self.canvas.itemconfig(self.circle, outline="#1e40c9", fill="#3855c9")
            self.canvas.itemconfig(self.text, text=self.observed_subject.name, fill="white")
            self.canvas.lift(self.circle)
            self.canvas.lift(self.text)
        else:
            self.canvas.itemconfig(self.circle, outline="#6b97c9", fill="#8bb0d9")
            self.canvas.itemconfig(self.text, text=self.observed_subject.name, fill="black")

        self.canvas.reset_scroll_region()

    def destroy(self):
        """
        Removes the node from the canvas.
        """
        self.canvas.delete(self.circle)
        self.canvas.delete(self.text)
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None

    def draw_node(self):
        """
        Places a circle on to the canvas with the according color scheme.
        """
        scale_factor = self.canvas.scale_factor
        canvas_x, canvas_y = self.canvas.coords_model_to_canvas(self.x, self.y)
        if self.is_selected:
            self.circle = self.canvas.create_circle(canvas_x, canvas_y, self.NODE_RADIUS * scale_factor,
                                                    outline="#1e40c9", fill="#3855c9", width=2, tags="node")
            self.text = self.canvas.create_text(canvas_x, canvas_y, text=self.observed_subject.name, fill="white")
        else:
            self.circle = self.canvas.create_circle(canvas_x, canvas_y, self.NODE_RADIUS * scale_factor,
                                                    outline="#6b97c9", fill="#8bb0d9", width=2, tags="node")
            self.text = self.canvas.create_text(canvas_x, canvas_y, text=self.observed_subject.name)

    def bind_node(self):
        """
        Creates all node bindings.
        """
        self.canvas.tag_bind(self.circle, OS.left_mouse_button, self.on_left_click)
        self.canvas.tag_bind(self.text, OS.left_mouse_button, self.on_left_click)
        self.canvas.tag_bind(self.circle, OS.shift_left_mouse_button, self.on_shift_left_click)
        self.canvas.tag_bind(self.text, OS.shift_left_mouse_button, self.on_shift_left_click)
        self.canvas.tag_bind(self.circle, OS.left_mouse_button_motion, self.move_node_on_drag)
        self.canvas.tag_bind(self.text, OS.left_mouse_button_motion, self.move_node_on_drag)

    def on_left_click(self, _) -> None:
        """
        Handles left click events.

        :param _: event
        """
        if self.button_bar.node_button_pressed:
            return
        elif self.button_bar.delete_button_pressed:
            self.controller.delete_component(self.observed_subject)
        elif self.button_bar.edge_button_pressed:
            from View.GUI.Windows.GraphWindow.EdgeView import EdgeView

            self.controller.on_component_click(self.observed_subject)
            if EdgeView.start_node is not None:
                self.controller.add_edge(EdgeView.start_node, self.observed_subject)
            EdgeView.start_node = self.observed_subject
            self.canvas.bind("<Motion>", lambda event: EdgeView.follow_mouse_cursor(self.canvas, event))
        elif self.button_bar.flow_button_pressed:
            self.on_flow_button_click()
        else:
            self.controller.on_component_click(self.observed_subject)

    def on_flow_button_click(self):
        """
        Handles the action of clicking on a flow.
        """
        from View.GUI.Windows.GraphWindow.FlowView.FlowView import FlowView

        self.controller.on_component_click(self.observed_subject)
        if FlowView.current_flow is None:
            if FlowView.start_node is not None:
                self.controller.add_flow(FlowView.start_node, self.observed_subject)
        else:
            self.controller.model_facade.insert_node_in_flow_path(
                FlowView.current_flow, self.observed_subject, is_edge_selected=True)
            self.controller.on_component_shift_click(FlowView.current_flow)

        FlowView.start_node = self.observed_subject
        self.canvas.bind("<Motion>", lambda event: FlowView.follow_mouse_cursor(self.canvas, event))

    def on_shift_left_click(self, _) -> None:
        """
        Handles Shift+Left click events.

        :param _: Shift+Left click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.edge_button_pressed or \
                self.button_bar.delete_button_pressed or self.button_bar.flow_button_pressed:
            return
        self.controller.on_component_shift_click(self.observed_subject)

    def move_node_on_drag(self, event) -> None:
        """
        Moves node to current mouse position when event is triggered.

        :param event: button click event
        """
        if self.button_bar.node_button_pressed or self.button_bar.delete_button_pressed or \
                self.button_bar.edge_button_pressed or self.button_bar.flow_button_pressed:
            return
        canvas_x, canvas_y = self.canvas.coords_event_to_canvas(event)
        old_x, old_y = self.canvas.coords_model_to_canvas(self.x, self.y)
        x_diff = canvas_x - old_x
        y_diff = canvas_y - old_y
        self.canvas.move(self.circle, x_diff, y_diff)
        self.canvas.move(self.text, x_diff, y_diff)
        self.x, self.y = self.canvas.coords_canvas_to_model(canvas_x, canvas_y)
        self.canvas.tag_bind(self.circle, '<ButtonRelease-1>', lambda _: self.end_node_drag())
        self.canvas.tag_bind(self.text, '<ButtonRelease-1>', lambda _: self.end_node_drag())

    def end_node_drag(self):
        """
        Handles releasing of a dragged node.
        """
        self.controller.model_facade.update_node_x_y(self.observed_subject, self.x, self.y)
        self.canvas.tag_unbind(self.circle, "<ButtonRelease-1>")
        self.canvas.tag_unbind(self.text, "<ButtonRelease-1>")
