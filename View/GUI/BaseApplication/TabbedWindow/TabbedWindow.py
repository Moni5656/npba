from tkinter import *
from tkinter.ttk import *

from View.GUI.BaseApplication.TabbedWindow.ContentFrame import ContentFrame
from View.GUI.BaseApplication.TabbedWindow.SelectionBar import SelectionBar
from View.GUI.CustomWidgets.DropLabel import DropLabel
from View.GUI.DragNDrop import DraggableContainer
from utils.utils import OS


class TabbedWindow(DraggableContainer):
    def __init__(self, selection_bar: SelectionBar, content_pane: Panedwindow, pane_index, pane_weight):

        self.selection_bar = selection_bar
        self.selection_bar.fun_end_drag = self.end_drag
        self.selection_bar.fun_start_drag = self.start_drag
        self.selection_bar.tabbed_window = self

        self.content_frame = ContentFrame(self, content_pane, pane_index, pane_weight)
        self._drop_here_widget = DropLabel(self.get_frame(), self)
        self.widget_names = {}

        # vars for drag and drop
        self.is_widget_visible_before_drag = False
        # move super to end, so all variables are initialized
        super().__init__()

    def get_frame(self):
        return self.content_frame.notebook

    def get_widget_name(self, widget) -> 'str':
        return self.widget_names[widget]

    def get_selected_widget(self) -> Widget:
        return self.content_frame.selected_widget

    def add_by_drag(self, widget, name):
        self._add(widget, name)
        # don't restore old widget after drag, use new one instead
        self.widget_before_drag = widget
        # don't hide widget after getting added
        self.is_widget_visible_before_drag = True

    def remove_by_drag(self, widget):
        self.remove(widget)
        if self.widget_before_drag == widget:
            self.widget_before_drag = None

    def add_drag_bindings(self) -> None:
        self.content_frame.title_bar.bind(OS.left_mouse_button_motion, self.start_drag)
        self.content_frame.title_bar.bind(OS.left_mouse_button_release, self.end_drag)
        self.content_frame.title_bar.title_name.bind(OS.left_mouse_button_motion, self.start_drag)
        self.content_frame.title_bar.title_name.bind(OS.left_mouse_button_release, self.end_drag)

    def enter_drag_mode(self):
        self.is_widget_visible_before_drag = self.content_frame.is_visible
        self.widget_before_drag = self.get_selected_widget()
        self._add(self._drop_here_widget, "")
        self.select(self._drop_here_widget)

    def exit_drag_mode(self):
        self.remove(self._drop_here_widget)
        if self.widget_before_drag is not None:
            self.select(self.widget_before_drag)
        else:
            self.select_first_or_minimize()
        if not self.is_widget_visible_before_drag and self.content_frame.is_visible:
            self.deselect_all_buttons()
        self.widget_before_drag = None

    def add_widget(self, widget: Widget, name: str):
        self.add_and_select(widget, name)

    def _add(self, widget, name):
        """
        Adds a widget.

        :param widget: widget
        :param name: name of the widget
        """
        self.content_frame.notebook.add(widget)
        self.widget_names[widget] = name
        self.selection_bar.add(widget, name)

    def add_and_select(self, widget, name):
        """
        Adds and selects a widget.

        :param widget: widget
        :param name: name of the widget
        """
        self._add(widget, name)
        self.select(widget)

    def select_or_minimize(self, widget):
        """
        Selects or minimizes a widget based on the current selection state.

        :param widget: widget
        """
        if self.content_frame.selected_widget == widget and self.content_frame.is_visible:
            self.deselect_all_buttons()
        else:
            self.select(widget)

    def select(self, widget):
        """
        Selects a widget.

        :param widget: widget
        """
        name = self.get_widget_name(widget)
        self.content_frame.select(widget, name)
        self.selection_bar.select(widget)

    def restore(self):
        """
        Can be used to restore a frame, e.g., after minimizing.
        """
        self.content_frame.restore()

    def deselect_all_buttons(self):
        """
        Deselects all buttons.
        """
        self.content_frame.minimize()
        self.selection_bar.deselect_all_buttons()

    def remove(self, widget):
        """
        Removes a widget.

        :param widget: widget
        """
        del self.widget_names[widget]
        self.selection_bar.remove(widget)
        self.content_frame.remove(widget)

    def select_first_or_minimize(self):
        """
        Selects the first tab or minimizes window if no tabs are available.
        """
        if len(self.widget_names) > 0:
            self.select(list(self.widget_names.keys())[0])
        else:
            self.deselect_all_buttons()

    def destroy(self):
        """
        Destroys the tabbed window.
        """
        self._deregister_container()
