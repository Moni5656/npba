from abc import ABC, abstractmethod

from View.GUI.DragNDrop import DraggableContainer


class DropTarget(ABC):
    @abstractmethod
    def get_container(self) -> DraggableContainer:
        """
        Returns the draggable container.
        """
        raise NotImplementedError
