from abc import ABC, abstractmethod
from tkinter import Widget

from View.GUI.BaseApplication.Position import Position
from View.GUI.DragNDrop import DraggableWidget


class WindowInterface(DraggableWidget, ABC):

    @abstractmethod
    def __init__(self, parent, controller, network):
        self.controller = controller
        self.network = network
        _ = parent

    @staticmethod
    @abstractmethod
    def get_title() -> str:
        """
        Returns the window title.

        :return: window title
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_start_position() -> Position:
        """
        Returns the default layout position of a window.

        :return: layout position
        """
        raise NotImplementedError

    @staticmethod
    def get_importance():
        """
        A higher value indicates a higher importance. Default value is 0.

        :return: int defining the importance of the window
        """
        return 0

    def clone(self, new_parent: Widget) -> 'WindowInterface':
        return self.__class__(new_parent, self.controller, self.network)
