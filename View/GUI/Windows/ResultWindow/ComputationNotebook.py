import tkinter as tk

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.CustomWidgets.NotebookCloseableTabs import NotebookCloseableTabs
from View.GUI.Windows.ResultWindow.ComputationStatusBoard import ComputationStatusBoard
from View.Observer import Observer


class ComputationNotebook(NotebookCloseableTabs, Observer):

    def __init__(self, parent, computation, controller):
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        super().__init__(parent, color_notebook_bg=fg_color)

        self.add_widget(ComputationStatusBoard(self, computation, controller), "Status Board")
        self.results = []
        self.handler_id = None
        self.subscribed_results = []

        Observer.__init__(self, computation)
        for result in computation.results:
            if result.is_finished:
                self.results.append(result)
            else:
                result.subscribe(self)
                self.subscribed_results.append(result)
        self.handle_tasks()

    def update_(self, updated_component):
        if updated_component[1] == "finished_result":
            result = updated_component[0]
            self.results.append(result)

    def start_task_handler(self):
        """
        Starts the task handler.
        """
        self.handler_id = self.after(2000, self.handle_tasks)

    def handle_tasks(self):
        """
        Handles received results.
        """
        for result in list(self.results):
            self.add_result(result)
            self.results.remove(result)

        self.start_task_handler()

    def destroy(self):
        self.after_cancel(self.handler_id)
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        for result in self.subscribed_results:
            result.unsubscribe(self)
        self.subscribed_results.clear()
        super().destroy()

    def add_result(self, result):
        """
        Adds results to the notebook.

        :param result: result object
        """
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        textbox = ctk.CTkTextbox(self, fg_color=fg_color, bg_color=fg_color, wrap="word")
        textbox.insert(tk.END, result.result_text)
        self.add_widget(textbox, result.configuration_name)
