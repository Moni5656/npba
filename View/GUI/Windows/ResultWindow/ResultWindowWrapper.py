from tkinter import Widget

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.BaseApplication.Position import Position
from View.GUI.Windows import WindowInterface
from View.GUI.Windows.ResultWindow.ResultWindow import ResultWindow


class ResultWindowWrapper(WindowInterface, ctk.CTkFrame):

    @staticmethod
    def get_title() -> str:
        return "Results"

    @staticmethod
    def get_start_position() -> Position:
        return Position.TopLeft

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        bg_color = ThemeManager.theme["color_scale"]["outer"]
        ctk.CTkFrame.__init__(self, parent, fg_color=fg_color, bg_color=bg_color)

        self.result_window = ResultWindow(self, network, controller)
        self.result_window.pack(fill="both", expand=True, padx=3, pady=3)

    def clone(self, new_parent: Widget) -> 'WindowInterface':
        result_window_wrapper = ResultWindowWrapper(new_parent, self.controller, self.network)
        self.result_window.copy_to(result_window_wrapper.result_window)
        return result_window_wrapper
