import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.BaseApplication.TabbedWindow.NotebookTabless import NotebookTabless
from View.GUI.BaseApplication.TabbedWindow.TitleBar import TitleBar


class ContentFrame(ctk.CTkFrame):
    EVENT_MINIMIZE_TABBED_WINDOW = "<<OnTabbedWindowMinimize>>"
    EVENT_RESTORE_TABBED_WINDOW = "<<OnTabbedWindowRestore>>"

    def __init__(self, tabbed_window, content_pane, pane_index, pane_weight, **kw):
        color = ThemeManager.theme["color_scale"]["outer"]
        super().__init__(content_pane, fg_color=color, bg_color=color, **kw)
        self.content_pane = content_pane
        self.pane_index = pane_index
        self.pane_weight = pane_weight
        self.is_visible = False
        self.selected_widget = None

        self.restore()
        self.columnconfigure(0, weight=1)

        self.title_bar = TitleBar(tabbed_window, self)
        self.title_bar.grid(column=0, row=0, pady=(0, 3), sticky="nsew")
        self.rowconfigure(0, weight=0)

        self.notebook = NotebookTabless(self)
        self.notebook.grid(column=0, row=1, sticky="nsew")
        self.rowconfigure(1, weight=1)

    def set_name(self, name):
        """
        Set the name of the title bar.

        :param name: name
        """
        self.title_bar.set_name(name)

    def restore(self):
        """
        Restores a minimized window.
        """
        if self.is_visible:
            return
        self.is_visible = True
        if self.pane_index >= len(self.content_pane.panes()):
            self.content_pane.add(self, weight=self.pane_weight)
        else:
            self.content_pane.insert(self.pane_index, self, weight=self.pane_weight)
        self.content_pane.event_generate(ContentFrame.EVENT_RESTORE_TABBED_WINDOW)

    def select(self, widget, name):
        """
        Switch the content of a window.

        :param widget: new content widget
        :param name: name of the widget
        """
        self.restore()
        self.selected_widget = widget
        self.notebook.select(widget)
        self.set_name(name)

    def remove(self, widget):
        """
        Remove a content window from the frame.

        :param widget: widget which should be deleted
        """
        self.notebook.forget(widget)
        current_tab_name = self.notebook.select()
        self.selected_widget = None if current_tab_name == "" else self.nametowidget(current_tab_name)

    def minimize(self):
        """
        Minimizes the content of a frame.
        """
        if not self.is_visible:
            return
        self.is_visible = False
        self.content_pane.forget(self)
        self.content_pane.event_generate(ContentFrame.EVENT_MINIMIZE_TABBED_WINDOW)
