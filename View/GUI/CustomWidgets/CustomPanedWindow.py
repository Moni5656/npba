import tkinter.ttk as ttk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget


class CustomPanedWindow(ttk.PanedWindow, CustomWidget):

    def __init__(self, parent, color=None, **kwargs):
        if color is None:
            color = ThemeManager.theme["color_scale"]["outer"]
        self.background_color = color

        super().__init__(parent, style="CustomPane.TPanedwindow", **kwargs)
        CustomWidget.__init__(self, parent)

    def change_widget_style(self):
        bg = self.themed_color(self.background_color)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("CustomPane.TPanedwindow",
                        background=bg)
        self.configure(style="CustomPane.TPanedwindow")

    def destroy(self):
        self.remove_tracker()
        super().destroy()
