import io
import time
import tkinter as tk
from tkinter import Widget

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.BaseApplication.Position import Position
from View.GUI.Windows import WindowInterface
from View.Observer import Observer


class ErrorWindow(WindowInterface, ctk.CTkFrame, Observer):

    @staticmethod
    def get_title() -> str:
        return "Error Log"

    @staticmethod
    def get_start_position() -> Position:
        return Position.BottomLeft

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        bg_color = ThemeManager.theme["color_scale"]["outer"]
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        ctk.CTkFrame.__init__(self, parent, fg_color=fg_color, bg_color=bg_color)
        Observer.__init__(self, network)

        self.error_log = ctk.CTkTextbox(self, fg_color=fg_color, undo=True, wrap="word")
        self.error_log.grid(column=0, row=0, sticky="news", pady=3, padx=3)
        self.error_log.tag_config("error", foreground="#ff644e")

        clear_button = ctk.CTkButton(self, text="Clear", command=lambda: self.error_log.delete(0.0, tk.END))
        clear_button.grid(column=0, row=0, sticky="se", pady=20, padx=20)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def update_(self, updated_component):
        if updated_component[1] == "error":
            error = updated_component[0]
            with io.StringIO() as error_log:
                print(str(error), file=error_log)
                self.error_log.insert(tk.END, time.strftime("%H:%M:%S") + "\n", tags="error")
                self.error_log.insert(tk.END, error_log.getvalue() + "\n\n\n", tags="error")
                self.error_log.see(tk.END)

    def clone(self, new_parent: Widget) -> 'WindowInterface':
        error_window = ErrorWindow(new_parent, self.controller, self.network)
        error_window.error_log.insert(0.0, self.error_log.get(0.0, tk.END), tags="error")
        return error_window

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        super().destroy()
