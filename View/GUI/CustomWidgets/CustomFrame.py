import tkinter as tk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget


class CustomFrame(tk.Frame, CustomWidget):
    def __init__(self, parent, color=None, **kwargs):
        if color is None:
            color = ThemeManager.theme["color_scale"]["inner"]
        self.color = color
        super().__init__(parent, **kwargs)
        CustomWidget.__init__(self, parent)

    def change_widget_style(self):
        bg = self.themed_color(self.color)
        self.configure(background=bg)

    def destroy(self):
        self.remove_tracker()
        super().destroy()
