import tkinter as tk

import customtkinter as ctk
from customtkinter import ThemeManager

import View.GUI.Windows
from View.GUI.BaseApplication.Position import Position
from View.GUI.BaseApplication.TabbedWindow.ContentFrame import ContentFrame
from View.GUI.BaseApplication.TabbedWindow.SelectionBar import SelectionBar
from View.GUI.BaseApplication.TabbedWindow.TabbedWindow import TabbedWindow
from View.GUI.CustomWidgets.CustomPanedWindow import CustomPanedWindow
from View.GUI.CustomWidgets.NotebookCloseableTabs import NotebookCloseableTabs
from View.GUI.DragNDrop.DraggableContainer import DraggableContainer


class LayoutWindow(ctk.CTkFrame):
    WEIGHT_TOP = 10
    WEIGHT_1 = 1
    WEIGHT_2 = 10
    WEIGHT_3 = 5
    WEIGHT_BOTTOM = 1
    WEIGHT_4 = 1
    WEIGHT_5 = 1

    def __init__(self, parent, controller, network, **kw):
        color = ThemeManager.theme["color_scale"]["outer"]
        super().__init__(parent, bg_color=color, fg_color=color, **kw)

        self.controller = controller
        self.network = network

        self.control_1 = SelectionBar(self, tk.N)
        self.control_1.grid(column=0, row=0, padx=(0, 4), pady=0, sticky="nsew")
        self.columnconfigure(0, weight=0)

        self.control_3 = SelectionBar(self, tk.N)
        self.control_3.grid(column=3, row=0, padx=(4, 0), sticky="nsew")
        self.columnconfigure(3, weight=0)

        self.rowconfigure(0, weight=1)

        self.control_4 = SelectionBar(self, tk.W)
        self.control_4.grid(column=1, row=1, pady=(4, 0), sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.control_5 = SelectionBar(self, tk.E)
        self.control_5.grid(column=2, row=1, pady=(4, 0), sticky="nsew")
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=0)

        self.main_pane = CustomPanedWindow(self, orient=tk.VERTICAL)
        self.main_pane.grid(column=1, row=0, columnspan=2, sticky="nsew")

        self.top = CustomPanedWindow(self.main_pane, orient=tk.HORIZONTAL)
        self.main_pane.add(self.top, weight=LayoutWindow.WEIGHT_TOP)

        self.bottom = CustomPanedWindow(self.main_pane, orient=tk.HORIZONTAL)
        self.main_pane.add(self.bottom, weight=LayoutWindow.WEIGHT_BOTTOM)
        self.is_bottom_visible = True
        self.bottom_bindings()

        self.widget_container: 'list[DraggableContainer]' = []
        self.make_children()

    def bottom_bindings(self):
        """
        Create bindings for the bottom paned window.
        """
        # minimize or restore bottom window when its content changes
        self.bottom.bind(ContentFrame.EVENT_MINIMIZE_TABBED_WINDOW,
                         lambda _: self.minimize_bottom() if len(self.bottom.panes()) == 0 else ())
        self.bottom.bind(ContentFrame.EVENT_RESTORE_TABBED_WINDOW,
                         lambda _: self.add_bottom() if len(
                             self.bottom.panes()) > 0 and not self.is_bottom_visible else ())

    def add_bottom(self):
        """
        Adds a bottom paned window.
        """
        self.main_pane.add(self.bottom, weight=LayoutWindow.WEIGHT_BOTTOM)
        self.is_bottom_visible = True

    def minimize_bottom(self):
        """
        Minimizes the bottom paned window.
        """
        self.main_pane.forget(self.bottom)
        self.is_bottom_visible = False

    def make_children(self):
        """
        Creates container widgets.
        """
        main_pane = NotebookCloseableTabs(self.top, is_tabs_draggable=True)
        self.top.add(main_pane, weight=LayoutWindow.WEIGHT_2)
        self.widget_container.append(TabbedWindow(self.control_1, self.top, 0, LayoutWindow.WEIGHT_1))
        self.widget_container.append(main_pane)
        self.widget_container.append(TabbedWindow(self.control_3, self.top, 2, LayoutWindow.WEIGHT_3))
        self.widget_container.append(TabbedWindow(self.control_4, self.bottom, 0, LayoutWindow.WEIGHT_4))
        self.widget_container.append(TabbedWindow(self.control_5, self.bottom, 1, LayoutWindow.WEIGHT_5))

    def add_content(self, position: Position, content: tk.Widget, name: str):
        """
        Adds content to a container.

        :param position: position of the container
        :param content: widget
        :param name: name of the widget
        """
        container = self.widget_container[position]
        container.add_widget(content, name)

    def get_container_parent_at(self, position: Position) -> tk.Widget:
        """
        Get the parent of a container.

        :param position: position of the container
        :return: parent widget of the container
        """
        return self.widget_container[position].get_frame()

    def add_default_content(self):
        """
        Adds the default content to each container.
        """
        windows = View.GUI.Windows.get_available_windows()
        windows.sort(key=lambda w: w[0].get_importance())

        for window_class, title, position in windows:
            try:
                window = window_class(
                    parent=self.get_container_parent_at(position), controller=self.controller, network=self.network)
                self.add_content(position, window, title)
            except Exception as e:
                self.controller.model_facade.notify_error(e)
