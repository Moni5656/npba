import tkinter.ttk as ttk
from tkinter import *

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget


class CustomNotebook(ttk.Notebook, CustomWidget):
    _initialized = False

    def __init__(self, parent: Widget, color_tab=None, color_tab_text=None, color_tab_border=None,
                 color_tab_hover=None, color_tab_selected=None, color_notebook=None,
                 *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.style = ttk.Style()
        self.style_name = str(self)
        self.__initialize_custom_style()

        self.add_notebook_bindings()
        self.enable_traversal()

        if color_tab is None:
            color_tab = self.color("notebook_tab")
        self.color_tab = color_tab
        if color_tab_text is None:
            color_tab_text = self.color("notebook_tab_text")
        self.color_tab_text = color_tab_text
        if color_tab_border is None:
            color_tab_border = self.color("notebook_tab_border")
        self.color_tab_border = color_tab_border
        if color_tab_hover is None:
            color_tab_hover = self.color("notebook_tab_hover")
        self.color_tab_hover = color_tab_hover
        if color_tab_selected is None:
            color_tab_selected = self.color("notebook_tab_selected")
        self.color_tab_selected = color_tab_selected
        if color_notebook is None:
            color_notebook = ThemeManager.theme["color_scale"]["inner"]
        self.color_notebook = color_notebook

        CustomWidget.__init__(self, parent)

    @staticmethod
    def color(key):
        """
        Returns a color with a certain key from the theme JSON file.

        :param key: color key
        :return: color
        """
        return ThemeManager.theme["CustomNotebook"][key]

    def __initialize_custom_style(self) -> None:
        """
        Initializes ttk style.
        """
        self.style.layout(self.style_name, [(f"{self.style_name}.client", {"sticky": "news"})])
        self.style.layout(f"{self.style_name}.Tab", [
            (f"{self.style_name}.tab", {
                "sticky": "news",
                "children": [
                    (f"{self.style_name}.padding", {
                        "side": "top",
                        "sticky": "news",
                        "children": [
                            (f"{self.style_name}.focus", {
                                "side": "top",
                                "sticky": "news",
                                "children": [
                                    (f"{self.style_name}.label", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        self.style.configure(f'{self.style_name}.Tab', padding=[8, 2])

    def change_widget_style(self):
        self.style.theme_use("default")
        self.style.configure(f"{self.style_name}.Tab", background=self.themed_color(self.color_tab),
                             foreground=self.themed_color(self.color_tab_text),
                             bordercolor=self.themed_color(self.color_tab_border),
                             borderwidth=0)
        self.style.configure(f"{self.style_name}", background=self.themed_color(self.color_notebook),
                             borderwidth=0)
        self.style.map(f"{self.style_name}.Tab",
                       background=[('active', self.themed_color(self.color_tab_hover)),
                                   ('selected', self.themed_color(self.color_tab_selected))])
        self.configure(style=f"{self.style_name}")

    def add_notebook_bindings(self) -> None:
        """
        Disables switching tabs in notebooks by using the left and right key.
        """

        def _break(_):
            return "break"

        self.bind("<Left>", _break)
        self.bind("<Right>", _break)

    def destroy(self) -> None:
        self.remove_tracker()
        super().destroy()
