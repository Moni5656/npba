import abc

from customtkinter import AppearanceModeTracker


class CustomWidget:
    def __init__(self, parent):
        self.master = parent
        self.appearance_mode = AppearanceModeTracker.get_mode()
        AppearanceModeTracker.add(self.set_appearance_mode, self)
        self.change_widget_style()

    def set_appearance_mode(self, mode: str):
        """
        Sets the current appearance mode on appearance mode changes.
        :param mode: either "dark" or "light"
        """
        if mode.lower() == "dark":
            self.appearance_mode = 1
        else:
            self.appearance_mode = 0
        self.change_widget_style()

    @abc.abstractmethod
    def change_widget_style(self):
        """
        This method is called on each appearance mode change. Use this method to style your widgets for both appearance
        modes.
        """
        pass

    def remove_tracker(self):
        """
        Stops tracking appearance mode changes for the set_appearance_mode method.
        """
        AppearanceModeTracker.remove(self.set_appearance_mode)

    def themed_color(self, color, appearance_mode=None) -> str:
        """
        Returns a color matching the current appearance mode.
        :param color: a tuple of colors for light and dark mode
        :param appearance_mode: current appearance mode
        :return: color
        """
        if appearance_mode is None:
            appearance_mode = self.appearance_mode

        if isinstance(color, (tuple, list)) and len(color) > appearance_mode:
            return color[appearance_mode]
        else:
            return color
