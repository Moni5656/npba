from tkinter import Widget

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.BaseApplication.Position import Position
from View.GUI.Windows import WindowInterface
from View.GUI.Windows.PlotWindow.PlotWindow import PlotWindow


class PlotWindowWrapper(WindowInterface, ctk.CTkFrame):

    @staticmethod
    def get_title() -> str:
        return "Plots"

    @staticmethod
    def get_start_position() -> Position:
        return Position.BottomRight

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        bg_color = ThemeManager.theme["color_scale"]["outer"]
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        ctk.CTkFrame.__init__(self, parent, fg_color=fg_color, bg_color=bg_color)
        self.plot_window = PlotWindow(self, network)
        self.plot_window.pack(fill="both", expand=True, padx=3, pady=3)

    def clone(self, new_parent: Widget) -> 'WindowInterface':
        plot_window_wrapper = PlotWindowWrapper(new_parent, self.controller, self.network)
        for computation in self.plot_window.contained_computations.values():
            plot_window_wrapper.plot_window.add_computation(computation)
        return plot_window_wrapper
