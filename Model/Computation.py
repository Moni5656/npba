import time as time_mod
import uuid

from Model import Result
from Model.Subject import Subject


class Computation(Subject):

    def __init__(self):
        super().__init__()
        self.id = uuid.uuid4()
        self.results = []
        self.start_time = None
        self.end_time = None
        self.is_finished = False
        self.is_canceled = False

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
        Defines a start time.
        """
        self.start_time = time_mod.time()

    def set_end_time(self):
        """
        Defines an end time.
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
        Finishes the timer.
        """
        self.set_end_time()
        self.is_finished = True
        self.notify((self, "computation_finished"))

    def cancel(self):
        """
        Cancels the computation.
        """
        self.set_end_time()
        self.is_canceled = True
        for result in self.results:
            if not result.is_finished:
                result.cancel()
        self.notify((self, "computation_canceled"))

    def add_result(self, result: Result):
        """
        Appends results to a list of results.

        :param result: result object
        """
        self.results.append(result)
