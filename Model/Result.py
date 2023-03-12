import time as time_mod
import uuid
from typing import Any

import matplotlib.figure

from Model.Subject import Subject


class Result(Subject):

    def __init__(self, configuration_name: str, configuration_id: uuid.UUID):
        super().__init__()
        self.configuration_name = configuration_name
        self.configuration_id = configuration_id
        self.id = uuid.uuid4()
        self.is_finished = False
        self.is_canceled = False
        self.is_error = False
        self.result_text = ""
        self.plots: list[tuple[str, matplotlib.figure.Figure]] = []
        self.start_time = None
        self.end_time = None

    @staticmethod
    def get_timestamp(format_str, time) -> str:
        """
        Formats the time as demanded by the format string.

        :param format_str: string as in time.strftime()
        :param time: time in seconds elapsed since the epoch, as in time.time()
        :return: formatted time as string
        """
        return time_mod.strftime(format_str, time_mod.localtime(time))

    def set_start_time(self):
        """
        Sets the start time.
        """
        self.start_time = time_mod.time()

    def set_end_time(self):
        """
        Sets the end time.
        """
        if self.end_time is None:
            self.end_time = time_mod.time()

    def start(self):
        """
        Starts the computation.
        """
        self.set_start_time()

    def finish(self):
        """
        Finishes the computation.
        """
        self.set_end_time()
        self.is_finished = True

    def cancel(self):
        """
        Cancels the computation.
        """
        self.set_end_time()
        self.is_canceled = True
        self.notify((self, "canceled_result"))

    def error(self):
        """
        Handles errors during computations.
        """
        self.set_end_time()
        self.is_error = True
        self.notify((self, "error_result"))

    def append_result(self, value: Any, num_of_tabs=0, tab="        "):
        """
        Appends results to the current result object.

        :param value: results
        :param num_of_tabs: number of tabs
        :param tab: can be used to define a tab
        """
        result_text = str(value)
        if num_of_tabs > 0:
            result_text = (tab * num_of_tabs) + (tab * num_of_tabs).join(result_text.splitlines(keepends=True))
        self.result_text += result_text + "\n"

    def add_plot(self, fig: matplotlib.figure.Figure, display_name: str = "Plot"):
        """
        Adds a plot to the current result object.

        :param fig: plot
        :param display_name: name of the plot
        """
        self.plots.append((display_name, fig))
