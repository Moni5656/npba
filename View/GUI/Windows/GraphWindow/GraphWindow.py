from tkinter import Widget

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.Windows.GraphWindow.ButtonBar import ButtonBar
from View.GUI.Windows.GraphWindow.GraphCanvas import GraphCanvas
from View.GUI.Windows.WindowInterface import WindowInterface, Position


class GraphWindow(WindowInterface, ctk.CTkFrame):

    @staticmethod
    def get_title() -> str:
        return "Graph"

    @staticmethod
    def get_start_position() -> Position:
        return Position.Center

    @staticmethod
    def get_importance():
        return 5

    def __init__(self, parent, controller, network, move_to_center=True):
        WindowInterface.__init__(self, parent, controller, network)
        bg_color = ThemeManager.theme["color_scale"]["outer"]
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        ctk.CTkFrame.__init__(self, parent, fg_color=fg_color, bg_color=bg_color)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.graph_canvas = GraphCanvas(self, controller, network, move_to_center=move_to_center)

        self.graph_canvas.grid(column=0, row=0, sticky="news", padx=3, pady=3)
        self.button_bar = ButtonBar(self, self.graph_canvas)
        self.button_bar.grid(column=0, row=0, sticky="n", pady=5)
        self.graph_canvas.button_bar = self.button_bar
        self.graph_canvas.initial_setup()

    def clone(self, new_parent: Widget) -> 'WindowInterface':
        new_window = GraphWindow(new_parent, self.controller, self.network, move_to_center=False)
        new_window.graph_canvas.zoom_to(self.graph_canvas.scale_factor)

        old_x_middle = self.graph_canvas.canvasx(self.graph_canvas.winfo_width() / 2)
        old_y_middle = self.graph_canvas.canvasy(self.graph_canvas.winfo_height() / 2)
        old_x_model, old_y_model = self.graph_canvas.coords_canvas_to_model(old_x_middle, old_y_middle)
        # estimate screen mid as canvas is not yet drawn with correct width / height
        estimated_mid_x = int(new_window.graph_canvas.canvasx(new_parent.winfo_width() / 2))
        estimated_mid_y = int(new_window.graph_canvas.canvasy(new_parent.winfo_height() / 2))
        new_window.graph_canvas.move_canvas_to(old_x_model, old_y_model, estimated_mid_x, estimated_mid_y)

        return new_window
