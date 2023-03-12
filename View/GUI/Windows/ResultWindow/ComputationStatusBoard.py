import tkinter as tk

import customtkinter as ctk
from customtkinter import ThemeManager

from Model import Computation
from View.GUI.CustomWidgets.ScrolledFrame import ScrolledFrame
from View.Observer import Observer


class ComputationStatusBoard(ctk.CTkFrame, Observer):

    def __init__(self, parent, computation: Computation, controller):
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        super().__init__(parent, fg_color=fg_color, bg_color=fg_color)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        Observer.__init__(self, computation)
        self.subscribe_to_all_results()
        self.tasks = []
        self.controller = controller
        self._items = {}
        self.init_status()
        self.handler_id = None
        self.handle_tasks()

    def subscribe_to_all_results(self):
        """
        Subscribes to all results.
        """
        for result in self.observed_subject.results:
            result.subscribe(self)

    def update_(self, updated_component):
        message = updated_component[1]
        if message == "computation_finished" or message == "computation_canceled":
            computation = updated_component[0]
            self.tasks.append(computation)
        elif message == "finished_result" or message == "canceled_result" or message == "error_result":
            result = updated_component[0]
            self.tasks.append(result)

    def init_status(self):
        """
        Creates the status board.
        """
        content_frame = ScrolledFrame(self)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)
        content_frame.grid(column=0, row=0, sticky="news")

        content_frame.scrolled_frame.columnconfigure(0, weight=1)
        content_frame.scrolled_frame.columnconfigure(1, weight=1)
        content_frame.scrolled_frame.columnconfigure(2, weight=1)
        ctk.CTkLabel(content_frame.scrolled_frame, text="ID:").grid(column=0, row=0)
        ctk.CTkLabel(content_frame.scrolled_frame, text=str(self.observed_subject.id)).grid(column=1, row=0)

        if self.observed_subject.is_canceled:
            status = "Canceled"
            active = tk.DISABLED
            end_time_text = self.observed_subject.get_timestamp("%H:%M:%S", self.observed_subject.end_time)
        elif self.observed_subject.is_finished:
            status = "Finished"
            active = tk.DISABLED
            end_time_text = self.observed_subject.get_timestamp("%H:%M:%S", self.observed_subject.end_time)
        else:
            status = "Running"
            active = tk.NORMAL
            end_time_text = "--:--:--"

        ctk.CTkLabel(content_frame.scrolled_frame, text="Status").grid(column=0, row=1)
        self._items["status"] = label = ctk.CTkLabel(content_frame.scrolled_frame, text=status)
        label.grid(column=1, row=1)
        self._items["cancel_button"] = btn = ctk.CTkButton(self, text="Terminate Computation", state=active,
                                                           command=lambda: self.controller.cancel_computation(
                                                               self.observed_subject))
        btn.grid(column=0, row=0, sticky="es", pady=20, padx=20)

        start_time = self.observed_subject.get_timestamp("%H:%M:%S", self.observed_subject.start_time)

        ctk.CTkLabel(content_frame.scrolled_frame, text="Start Time").grid(column=0, row=2)
        ctk.CTkLabel(content_frame.scrolled_frame, text=start_time).grid(column=1, row=2)

        ctk.CTkLabel(content_frame.scrolled_frame, text="End Time").grid(column=0, row=3)
        self._items["end_time"] = label = ctk.CTkLabel(content_frame.scrolled_frame, text=end_time_text)
        label.grid(column=1, row=3)

        offset = 4
        for index, result in enumerate(self.observed_subject.results):
            if result.is_error:
                status = "Error"
            elif result.is_canceled:
                status = "Canceled"
            elif result.is_finished:
                status = "Finished"
            else:
                status = "Running"
            ctk.CTkLabel(content_frame.scrolled_frame, text=result.configuration_name).grid(column=0,
                                                                                            row=offset + index)
            self._items[result] = label = ctk.CTkLabel(content_frame.scrolled_frame, text=status)
            label.grid(column=1, row=offset + index)

    def update_status(self):
        """
        Updates the status board.
        """
        if self.observed_subject.is_canceled:
            status = "Canceled"
        elif self.observed_subject.is_finished:
            status = "Finished"
        else:
            status = "Running"

        self._items["status"].configure(text=status)
        if self.observed_subject.end_time is not None:
            end_time = self.observed_subject.get_timestamp("%H:%M:%S", self.observed_subject.end_time)
            self._items["end_time"].configure(text=end_time)

        active = tk.DISABLED if self.observed_subject.is_finished else tk.NORMAL
        self._items["cancel_button"].configure(state=active)

        for result in self.observed_subject.results:
            if result.is_error:
                status = "Error"
            elif result.is_canceled:
                status = "Canceled"
            elif result.is_finished:
                status = "Finished"
            else:
                status = "Running"
            self._items[result].configure(text=status)

    def start_task_handler(self):
        """
        Starts the task handler.
        """
        self.handler_id = self.after(2000, self.handle_tasks)

    def handle_tasks(self):
        """
        Handles received updates.
        """
        if len(self.tasks) > 0:
            self.update_status()
        self.tasks.clear()
        self.start_task_handler()

    def destroy(self):
        self.after_cancel(self.handler_id)
        if isinstance(self.observed_subject, Computation):
            for result in self.observed_subject.results:
                result.unsubscribe(self)
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        super().destroy()
