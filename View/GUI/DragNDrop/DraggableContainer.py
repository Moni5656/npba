from abc import abstractmethod
from tkinter import Event
from tkinter import Widget
from typing import Optional

from View.GUI.DragNDrop.DraggableWidget import DraggableWidget
from View.GUI.DragNDrop.DropTarget import DropTarget
from utils import utils


class DraggableContainer(DropTarget):
    DRAGGED_WIDGET = None
    REGISTERED_CONTAINER = []

    def __init__(self) -> None:
        self.is_dragged = False
        self.widget_before_drag = None
        self.add_drag_bindings()
        self._register_container()

    def get_container(self):
        return self

    @abstractmethod
    def get_frame(self) -> Widget:
        """
        Returns the frame of the container.

        :return: widget
        """
        pass

    @abstractmethod
    def get_widget_name(self, widget: Widget) -> str:
        """
        Returns the name of the widget.

        :param widget: widget
        :return: name
        """
        pass

    @abstractmethod
    def get_selected_widget(self) -> Widget:
        """
        Returns the selected widget.

        :return: widget
        """
        pass

    @abstractmethod
    def add_widget(self, widget: Widget, name: str):
        """
        Adds a widget to the container.

        :param widget: widget
        :param name: name of the widget
        """
        pass

    @abstractmethod
    def add_by_drag(self, widget: Widget, name: str) -> None:
        """
        Adds a widget to the container by handling a drag and drop event.

        :param widget: widget
        :param name: name of the widget
        """
        pass

    @abstractmethod
    def remove_by_drag(self, widget: Widget) -> None:
        """
        Removes a widget from the old container.

        :param widget: widget
        """
        pass

    @abstractmethod
    def enter_drag_mode(self) -> None:
        """
        Enters the drag mode.
        """
        pass

    @abstractmethod
    def exit_drag_mode(self) -> None:
        """
        Exits the drag mode.
        """
        pass

    @abstractmethod
    def add_drag_bindings(self) -> None:
        """
        Adds the relevant bindings for drag and drop.
        """
        pass

    def move_widget_to(self: 'DraggableContainer', target: 'DraggableContainer',
                       moved_widget: 'DraggableWidget') -> None:
        """
        Moves a widget to another container.

        :param target: target container
        :param moved_widget: the moved widget
        """
        name = self.get_widget_name(moved_widget)
        new_widget = moved_widget.clone(target.get_frame())
        target.add_by_drag(new_widget, name)
        self.remove_by_drag(moved_widget)
        moved_widget.destroy()

    def start_drag(self, event) -> None:
        """
        Start the drag and drop process.

        :param event: event triggering the drag and drop process
        """
        if self.is_dragged:
            return
        self.is_dragged = True
        DraggableWidget.DRAGGED_WIDGET = self.get_selected_widget()
        DraggableContainer.notify_drag_start()
        event.widget.config(cursor=DraggableWidget.CURSOR_DRAG)

    def end_drag(self: 'DraggableContainer', event: 'Event') -> None:
        """
        Ends the drag and drop process.

        :param event: event triggering the end of the drag and drop process
        """
        if not self.is_dragged:
            return
        self.is_dragged = False

        event.widget.configure(cursor=DraggableWidget.CURSOR_DEFAULT)

        x, y = event.widget.winfo_pointerxy()
        drop_target = event.widget.winfo_containing(x, y)

        target_container: Optional[DraggableContainer] = None
        if isinstance(drop_target, DropTarget):
            target_container = drop_target.get_container()

        try:
            if target_container is None:
                raise ValueError(f"drag and drop ended on unknown widget: {drop_target}")
            else:
                self.move_widget_to(target_container, DraggableWidget.DRAGGED_WIDGET)

        finally:
            DraggableWidget.DRAGGED_WIDGET = None
            DraggableContainer.notify_drag_end()

    def _register_container(self):
        """
        Registers a container.
        """
        self.REGISTERED_CONTAINER.append(self)

    def _deregister_container(self):
        """
        Deregisters a container.
        """
        if self in self.REGISTERED_CONTAINER:
            self.REGISTERED_CONTAINER.remove(self)

    @staticmethod
    def notify_drag_start():
        """
        Notifies every draggable container about the start of the drag and drop process.
        """
        container: DraggableContainer
        for container in DraggableContainer.REGISTERED_CONTAINER:
            try:
                container.enter_drag_mode()
            except Exception as error:
                utils.print_exception_traceback(error)

    @staticmethod
    def notify_drag_end():
        """
        Notifies every draggable container about the end of the drag and drop process.
        """
        container: DraggableContainer
        for container in DraggableContainer.REGISTERED_CONTAINER:
            try:
                container.exit_drag_mode()
            except Exception as error:
                utils.print_exception_traceback(error)
