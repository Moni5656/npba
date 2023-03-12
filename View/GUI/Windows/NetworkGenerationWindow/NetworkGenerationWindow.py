from tkinter import Widget

from View.GUI.BaseApplication.Position import Position
from View.GUI.CustomWidgets.CustomNotebook import CustomNotebook
from View.GUI.Windows.NetworkGenerationWindow.BasicGeneration import BasicGeneration
from View.GUI.Windows.NetworkGenerationWindow.FlowGeneration import FlowGeneration
from View.GUI.Windows.NetworkGenerationWindow.NetworkxGeneration import NetworkxGeneration
from View.GUI.Windows.WindowInterface import WindowInterface


class NetworkGenerationWindow(WindowInterface, CustomNotebook):

    @staticmethod
    def get_title() -> str:
        return "Network Generation"

    @staticmethod
    def get_start_position() -> Position:
        return Position.TopRight

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        CustomNotebook.__init__(self, parent)

        self.basic_generation = BasicGeneration(self, controller)
        self.add(self.basic_generation, text="Basic")
        self.networkx_generation = NetworkxGeneration(self, controller=controller)
        self.add(self.networkx_generation, text="Advanced: NetworkX")
        self.flow_generation = FlowGeneration(self, controller=controller)
        self.add(self.flow_generation, text="Flows")

    def clone(self, new_parent: Widget) -> 'WindowInterface':
        new_window = NetworkGenerationWindow(new_parent, self.controller, self.network)
        self.basic_generation.clone_to(new_window.basic_generation)
        self.networkx_generation.clone_to(new_window.networkx_generation)
        self.flow_generation.clone_to(new_window.flow_generation)
        return new_window
