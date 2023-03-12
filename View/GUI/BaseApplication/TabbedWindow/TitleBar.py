from idlelib.tooltip import Hovertip
from tkinter import W, E

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.DragNDrop import DraggableContainer, DraggableWidget, DropTarget


class TitleBar(ctk.CTkFrame, DropTarget):

    def __init__(self, tabbed_window, parent, **kw):
        color = ThemeManager.theme["ContentWindowTitleBar"]["titlebar"]
        super().__init__(parent, fg_color=color, **kw)
        self.tabbed_window = tabbed_window
        self.title_name = ctk.CTkLabel(self, text="", anchor="w", padx=5)
        self.title_name.grid(column=0, row=0, sticky=W)
        self.columnconfigure(0, weight=1)

        color = ThemeManager.theme["ContentWindowTitleBar"]["minimize_button"]
        hover = ThemeManager.theme["ContentWindowTitleBar"]["minimize_button_hover"]
        title_min_btn = ctk.CTkButton(self, text="-", width=2, fg_color=color, bg_color=color, hover_color=hover,
                                      command=tabbed_window.deselect_all_buttons)
        title_min_btn.grid(column=1, row=0, sticky=E)
        Hovertip(title_min_btn, text="Minimize Window", hover_delay=500)
        self.columnconfigure(1, weight=1)
        self.configure(cursor=DraggableWidget.CURSOR_DRAG)

    def set_name(self, name):
        """
        Sets the name of the title bar.

        :param name: name
        """
        self.title_name.configure(text=name)

    def configure(self, **kwargs):
        kwargs["cursor"] = DraggableWidget.CURSOR_DRAG
        super().configure(**kwargs)

    def get_container(self) -> DraggableContainer:
        return self.tabbed_window

    def destroy(self):
        self.tabbed_window.destroy()
        super().destroy()
