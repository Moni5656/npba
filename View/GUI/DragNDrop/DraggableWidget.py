from abc import ABC, abstractmethod
from tkinter import Widget


class DraggableWidget(Widget, ABC):
    # cursors: https://www.tcl.tk/man/tcl8.7/TkCmd/cursors.html
    CURSOR_DRAG = "fleur"

    CURSOR_DEFAULT = ""
    DRAGGED_WIDGET = None

    @abstractmethod
    def clone(self, new_parent: Widget) -> 'DraggableWidget':
        """
        Returns a new Instance of the class in a new parent widget.

        :param self: old instance of the class
        :param new_parent: the new parent widget
        :return: the new instance, copying the old instance
        """
        raise NotImplementedError("Extend the DraggableWidget class for drag and drop to work")
