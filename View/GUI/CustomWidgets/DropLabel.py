import tkinter as tk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget
from View.GUI.DragNDrop import DropTarget


class DropLabel(tk.Label, CustomWidget, DropTarget):
    def __init__(self, parent, container) -> None:
        super().__init__(parent, text="Drop Here", anchor=tk.CENTER)
        self._container = container
        CustomWidget.__init__(self, parent)

    def destroy(self) -> None:
        self.remove_tracker()
        super().destroy()

    def change_widget_style(self):
        bg_color = self.themed_color(ThemeManager.theme["DropHereLabel"]["background_color"])
        text_color = self.themed_color(ThemeManager.theme["DropHereLabel"]["text_color"])
        self.configure(background=bg_color, foreground=text_color)

    def get_container(self):
        return self._container
