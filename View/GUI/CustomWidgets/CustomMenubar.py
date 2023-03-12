import tkinter as tk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget
from utils.utils import OS


class CustomMenubar(tk.Menu, CustomWidget):

    def __init__(self, parent):
        self.number_of_entries = 0
        super().__init__(parent)
        CustomWidget.__init__(self, parent)

    def add_cascade(self, **kwargs) -> None:
        if OS.MacOS:
            super().add_cascade(**kwargs)
        else:
            self.number_of_entries += 1
            bg = self.themed_color(ThemeManager.theme["CustomMenu"]["background_color"])
            fg = self.themed_color(ThemeManager.theme["CustomMenu"]["text_color"])
            hover_bg = self.themed_color(ThemeManager.theme["CustomMenu"]["background_hover_color"])
            hover_fg = self.themed_color(ThemeManager.theme["CustomMenu"]["text_hover_color"])

            super().add_cascade(foreground=fg, background=bg, activebackground=hover_bg, activeforeground=hover_fg,
                                **kwargs)

    def change_widget_style(self):
        if OS.MacOS:
            return
        bg = self.themed_color(ThemeManager.theme["CustomMenu"]["background_color"])
        fg = self.themed_color(ThemeManager.theme["CustomMenu"]["text_color"])
        hover_bg = self.themed_color(ThemeManager.theme["CustomMenu"]["background_hover_color"])
        hover_fg = self.themed_color(ThemeManager.theme["CustomMenu"]["text_hover_color"])
        self.configure(background=bg, foreground=fg, activebackground=hover_bg, activeforeground=hover_fg)
        for entry in range(0, self.number_of_entries):
            self.entryconfig(entry, background=bg, foreground=fg, activebackground=hover_bg, activeforeground=hover_fg)

    def destroy(self):
        self.remove_tracker()
        super().destroy()
