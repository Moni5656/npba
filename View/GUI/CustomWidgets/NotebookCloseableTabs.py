import tkinter.ttk as ttk
from tkinter import *

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget
from View.GUI.CustomWidgets.DropLabel import DropLabel
from View.GUI.DragNDrop import DraggableContainer
from utils.utils import OS


class NotebookCloseableTabs(ttk.Notebook, DraggableContainer, CustomWidget):
    """A ttk Notebook with close buttons on each tab. Parts taken and modified from:
    https://stackoverflow.com/a/39459376
    """

    def __init__(self, parent: Widget, is_tabs_draggable=False, color_tab_bg=None, color_tab_fg=None,
                 color_tab_border=None, color_tab_active=None, color_tab_selected=None, color_notebook_bg=None,
                 *args, **kwargs) -> None:
        self.is_tabs_draggable = is_tabs_draggable
        super().__init__(parent, *args, **kwargs)
        self._drop_here_widget = DropLabel(self.get_frame(), self)

        self.style = ttk.Style()
        self.style_name = str(self)
        self.__initialize_custom_style()
        DraggableContainer.__init__(self)

        self.grid(column=0, row=0, sticky="nsew")
        self.add_notebook_bindings()
        self.enable_traversal()

        if color_tab_bg is None:
            color_tab_bg = self.color("notebook_tab")
        self.color_tab_background = color_tab_bg
        if color_tab_fg is None:
            color_tab_fg = self.color("notebook_tab_text")
        self.color_tab_foreground = color_tab_fg
        if color_tab_border is None:
            color_tab_border = self.color("notebook_tab_border")
        self.color_tab_border = color_tab_border
        if color_tab_active is None:
            color_tab_active = self.color("notebook_tab_hover")
        self.color_tab_active = color_tab_active
        if color_tab_selected is None:
            color_tab_selected = self.color("notebook_tab_selected")
        self.color_tab_selected = color_tab_selected
        if color_notebook_bg is None:
            color_notebook_bg = ThemeManager.theme["color_scale"]["outer"]
        self.color_notebook_background = color_notebook_bg

        CustomWidget.__init__(self, parent)

    @staticmethod
    def color(key):
        """
        Returns a color with a certain key from the theme JSON file.

        :param key: color key
        :return: color
        """
        return ThemeManager.theme["CustomNotebook"][key]

    def change_widget_style(self):
        self.style.theme_use("default")
        self.style.configure(f"{self.style_name}.Tab", background=self.themed_color(self.color_tab_background),
                             foreground=self.themed_color(self.color_tab_foreground),
                             bordercolor=self.themed_color(self.color_tab_border),
                             borderwidth=0)
        self.style.configure(f"{self.style_name}", background=self.themed_color(self.color_notebook_background),
                             borderwidth=0)
        self.style.map(f"{self.style_name}.Tab",
                       background=[('active', self.themed_color(self.color_tab_active)),
                                   ('selected', self.themed_color(self.color_tab_selected))])
        self.configure(style=f"{self.style_name}")

    def get_frame(self) -> Widget:
        return self

    def get_widget_name(self, widget: Widget) -> 'str':
        return self.tab(widget)['text']

    def get_selected_widget(self) -> Widget:
        current_tab_name = self.select()
        widget = None if current_tab_name == "" else self.nametowidget(current_tab_name)
        return widget

    def add_widget(self, widget: Widget, name: str):
        self.add(widget, text=name)
        if self.is_tabs_draggable:
            self.select(widget)

    def add_by_drag(self, widget: Widget, name: str) -> None:
        self.add_widget(widget, name)
        self.widget_before_drag = widget

    def remove_by_drag(self, widget: Widget) -> None:
        self.forget(widget)
        # widget always was selected when moved away
        self.widget_before_drag = None

    def enter_drag_mode(self) -> None:
        if self.is_tabs_draggable:
            self.widget_before_drag = self.get_selected_widget()
            self.add_widget(self._drop_here_widget, "  ")
            self.select(self._drop_here_widget)

    def exit_drag_mode(self) -> None:
        if self.is_tabs_draggable:
            self.hide(self._drop_here_widget)
            if self.widget_before_drag is not None:
                self.select(self.widget_before_drag)

    def add_drag_bindings(self) -> None:
        if self.is_tabs_draggable:
            self.bind(OS.left_mouse_button_motion, lambda e: self.start_drag(e))
            self.bind(OS.left_mouse_button_release, lambda e: self.end_drag(e), add=True)

    def remove(self, widget: Widget) -> None:
        """
        Removes a widget from the notebook.

        :param widget: widget
        """
        widget.destroy()
        self.event_generate("<<NotebookTabClosed>>")

    def add_notebook_bindings(self) -> None:
        """
        Binds the close function to the notebook.
        """
        self.bind(OS.left_mouse_button, self.on_close_press)
        self.bind(OS.left_mouse_button_release, self.on_close_release, add=True)

        def _break(_):
            return "break"

        self.bind("<Left>", _break)
        self.bind("<Right>", _break)

    def start_drag(self, event) -> None:
        if self.get_selected_widget() is None:
            return
        else:
            super().start_drag(event)

    def on_close_press(self, event: Event) -> str:
        """
        Called when the close button is pressed.
        """
        element = self.identify(event.x, event.y)

        if "close_icon" in element:
            self.state(['pressed'])
            return "break"

    def on_close_release(self, event: Event) -> None:
        """
        Called when the button is released.
        """
        element = self.identify(event.x, event.y)
        if "close_icon" not in element or not self.instate(['pressed']):
            return

        index = self.index('@%d,%d' % (event.x, event.y))
        widget = self.nametowidget(self.tabs()[index])
        self.remove(widget)
        self.state(["!pressed"])

    def __initialize_custom_style(self) -> None:
        """
        Initializes a custom style for the notebook.
        """
        self.style.theme_use("default")
        self.images = (
            PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            PhotoImage("img_close_hover", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        if "close_icon" not in self.style.element_names():
            self.style.element_create("close_icon", "image", "img_close",
                                      ("active", "pressed", "!disabled", "img_close_hover"),
                                      ("active", "!disabled", "img_close_hover"), border=8, sticky='')

        self.style.layout(self.style_name, [(f"{self.style_name}.client", {"sticky": "nswe"})])
        self.style.layout(f"{self.style_name}.Tab", [
            (f"{self.style_name}.tab", {
                "sticky": "nswe",
                "children": [
                    (f"{self.style_name}.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            (f"{self.style_name}.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    (f"{self.style_name}.label", {"side": "left", "sticky": ''}),
                                    (f"{self.style_name}.close_icon", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        self.style.configure(f'{self.style_name}.Tab', padding=[4, 0])

    def destroy(self) -> None:
        self.remove_tracker()
        self._deregister_container()
        super().destroy()
