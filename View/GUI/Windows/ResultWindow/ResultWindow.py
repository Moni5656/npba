import tkinter as tk
from tkinter import Widget

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.CustomWidgets.NotebookCloseableTabs import NotebookCloseableTabs
from View.GUI.Windows.ResultWindow.ComputationNotebook import ComputationNotebook
from View.Observer import Observer


class ResultWindow(NotebookCloseableTabs, Observer):
    INSTRUCTION_TEXT = "To obtain results:\n" \
                       "        1. Create a network in the graph view.\n" \
                       "        2. Add a configuration in the configuration view.\n" \
                       "        3. [Optional] Adjust parameters in the parameter view.\n" \
                       "        4. Press the run button in the graph view to compute results.\n" \
                       "Furthermore, you can find plots, based on the results, in the plot view."

    def __init__(self, root_window, network, controller):
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        super().__init__(root_window, color_notebook_bg=fg_color)

        self.controller = controller
        self.instruction_text_window = ctk.CTkTextbox(self, fg_color=fg_color, bg_color=fg_color, undo=True,
                                                      wrap="word")
        self.add_instruction_tab()
        self.displayed_computations = {}

        Observer.__init__(self, network)

    def add_instruction_tab(self):
        """
        Adds an instruction tab to the notebook.
        """
        self.instruction_text_window.insert(tk.END, self.INSTRUCTION_TEXT)
        self.add_widget(self.instruction_text_window, "Instructions")

    def update_(self, updated_component):
        if updated_component[1] == "computation_started":
            computation = updated_component[0]
            self.add_computation(computation)

    def add_computation(self, computation):
        """
        Adds a computation tab to the notebook.

        :param computation: computation object
        """
        if self.instruction_text_window is not None:
            self.remove(self.instruction_text_window)
            self.instruction_text_window = None
        computation_tab = ComputationNotebook(self, computation, self.controller)
        timestamp = computation.get_timestamp("%H:%M:%S", computation.start_time)
        self.add_widget(computation_tab, timestamp)
        self.select(computation_tab)
        self.displayed_computations[computation_tab] = computation

    def remove(self, widget: Widget) -> None:
        if widget in self.displayed_computations:
            del self.displayed_computations[widget]
        super().remove(widget)

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        self.displayed_computations.clear()
        super().destroy()

    def copy_to(self, result_window):
        """
        Clones the result window to another window.

        :param result_window: new result window
        """
        for computation in self.displayed_computations.values():
            result_window.add_computation(computation)
