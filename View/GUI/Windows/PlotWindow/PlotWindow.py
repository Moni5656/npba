from tkinter import Widget

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.NotebookCloseableTabs import NotebookCloseableTabs
from View.GUI.Windows.PlotWindow.ComputationNotebook import ComputationNotebook
from View.Observer import Observer


class PlotWindow(NotebookCloseableTabs, Observer):

    def __init__(self, root_window, network):
        self.contained_computations = {}
        Observer.__init__(self, network)
        super().__init__(root_window, color_notebook_bg=ThemeManager.theme["color_scale"]["inner"])

    def update_(self, updated_component):
        if updated_component[1] == "computation_started":
            computation = updated_component[0]
            self.add_computation(computation)

    def add_computation(self, computation):
        """
        Adds a tab for a computation object.

        :param computation: computation object
        """
        computation_tab = ComputationNotebook(self, computation)
        timestamp = computation.get_timestamp("%H:%M:%S", computation.start_time)
        self.add_widget(computation_tab, timestamp)
        self.select(computation_tab)
        self.contained_computations[computation_tab] = computation

    def remove(self, widget: Widget) -> None:
        if widget in self.contained_computations:
            del self.contained_computations[widget]
        super().remove(widget)

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        self.contained_computations.clear()
        super().destroy()
