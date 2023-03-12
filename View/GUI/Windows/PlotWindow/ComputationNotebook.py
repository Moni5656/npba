from customtkinter import ThemeManager

from View.GUI.CustomWidgets.NotebookCloseableTabs import NotebookCloseableTabs
from View.GUI.Windows.PlotWindow.ResultNotebook import ResultNotebook
from View.Observer import Observer


class ComputationNotebook(NotebookCloseableTabs, Observer):

    def __init__(self, root_window, computation):
        super().__init__(root_window, color_notebook_bg=ThemeManager.theme["color_scale"]["inner"])

        self.ready_results = []
        self.subscribed_results = []
        Observer.__init__(self, computation)
        for result in computation.results:
            if result.is_finished:
                self.add_result(result)
            else:
                result.subscribe(self)
                self.subscribed_results.append(result)
        self.handler_id = None
        self.start_task_handler()

    def update_(self, updated_component):
        if updated_component[1] == "finished_result":
            result = updated_component[0]
            self.add_result_to_queue(result)

    def add_result_to_queue(self, result):
        self.ready_results.append(result)
        result.unsubscribe(self)
        self.subscribed_results.remove(result)

    def start_task_handler(self):
        self.handler_id = self.after(2000, self.handle_tasks)

    def handle_tasks(self):
        results_to_delete = []
        for result in self.ready_results:
            self.add_result(result)
            results_to_delete.append(result)
        for result in results_to_delete:
            self.ready_results.remove(result)

        self.start_task_handler()

    def add_result(self, result):
        self.add_widget(ResultNotebook(self, result), result.configuration_name)

    def destroy(self):
        self.after_cancel(self.handler_id)
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        for result in self.subscribed_results:
            result.unsubscribe(self)
        self.subscribed_results.clear()
        super().destroy()
