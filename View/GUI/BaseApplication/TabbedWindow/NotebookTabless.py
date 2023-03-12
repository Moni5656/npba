import tkinter as tk
import tkinter.ttk as ttk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget


class NotebookTabless(ttk.Notebook, CustomWidget):
    """A ttk Notebook without a tab bar. Taken and modified from:
    https://stackoverflow.com/questions/26923010/how-do-i-hide-the-entire-tab-bar-in-a-tkinter-ttk-notebook-widget """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.style = ttk.Style()
        self.style_name = str(self)
        CustomWidget.__init__(self, parent)
        self.configure(style=self.style_name)

    def __initialize_custom_style(self, appearance_mode=None) -> None:
        """
        Initializes a custom Tkinter style.

        :param appearance_mode: current appearance mode
        """
        self.style.layout(self.style_name, [(f"{self.style_name}.client", {"sticky": "nswe"})])
        self.style.layout(f"{self.style_name}.Tab", [])
        self.style.configure(self.style_name, borderwidth=0)
        background_color = ThemeManager.theme["color_scale"]["outer"]
        self.style.configure(self.style_name, background=self.themed_color(background_color, appearance_mode),
                             borderwidth=0)

    def change_widget_style(self):
        self.__initialize_custom_style()

    def destroy(self) -> None:
        self.remove_tracker()
        super().destroy()
