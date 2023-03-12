import customtkinter as ctk
from customtkinter import ThemeManager

from Controller.GUI.GUIController import GUIController


class EntryPopup(ctk.CTkEntry):
    """Taken from https://stackoverflow.com/a/18815802"""

    def __init__(self, parent, start_text, set_callback=lambda v: ()):
        bg_color = ThemeManager.theme["CustomTreeView"]["background_color"]
        super().__init__(parent, bg_color=bg_color)
        self.callback = set_callback

        self.insert(0, start_text)

        self.after(50, self.focus)
        self.select_range(0, "end")
        self.bind("<Return>", lambda _: self.set_value())
        self.bind("<Escape>", lambda _: (self.master.focus_force(), self.destroy()))
        self.bind("<FocusOut>", lambda _: self.destroy())

    def set_value(self, close_on_error=False):
        """
        Sets the value of an entry.

        :param close_on_error: whether the entry popup should be closed on errors
        """
        new_value = self.get()
        try:
            self.callback(new_value)
        except ValueError:
            GUIController.color_entry_border(self)
            if not close_on_error:
                return
        self.master.focus_force()
        self.destroy()
