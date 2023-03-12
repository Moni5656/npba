import tkinter as tk

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.BaseApplication.TabbedWindow.SelectionBarButton import SelectionBarButton
from View.GUI.DragNDrop import DraggableContainer, DropTarget
from utils.utils import OS


class SelectionBar(ctk.CTkFrame, DropTarget):

    def __init__(self, parent, orientation):
        color = ThemeManager.theme["SelectionBar"]["background"]
        super().__init__(parent, fg_color=color, bg_color=color)
        self.buttons = {}
        self.orientation = orientation
        self.angle = 270 if orientation == tk.N else 0

        self.tabbed_window = None
        self.fun_start_drag = None
        self.fun_end_drag = None

    def add(self, widget, name):
        """
        Adds a widget to the selection bar.

        :param widget: widget
        :param name: widget name
        """
        b = SelectionBarButton(self, name, command=lambda _: self.tabbed_window.select_or_minimize(widget),
                               angle=self.angle)
        self.buttons[widget] = b
        if self.angle == 0:
            b.pack(side=tk.RIGHT if self.orientation == tk.E else tk.LEFT)
        else:
            b.pack(side=tk.TOP)
        b.bind(OS.left_mouse_button_motion, self.fun_start_drag)
        b.bind(OS.left_mouse_button_release, self.fun_end_drag)

    def select(self, widget):
        """
        Handles selection of a widget.

        :param widget: widget
        """
        self.deselect_all_buttons()
        clicked_button = self.buttons[widget]
        clicked_button.set_selected()

    def deselect_all_buttons(self):
        """
        Deselects all selection bar buttons.
        """
        for button in self.buttons.values():
            button.set_inactive()

    def remove(self, widget):
        """
        Removes a widget from the selection bar.

        :param widget: widget
        """
        b = self.buttons[widget]
        del self.buttons[widget]
        b.destroy()

    def get_container(self) -> DraggableContainer:
        return self.tabbed_window
