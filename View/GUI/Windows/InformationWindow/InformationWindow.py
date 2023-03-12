import tkinter as tk

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.BaseApplication.Position import Position
from View.GUI.Windows import WindowInterface
from View.Observer import Observer


class InformationWindow(WindowInterface, ctk.CTkFrame, Observer):

    @staticmethod
    def get_title() -> str:
        return "Information"

    @staticmethod
    def get_start_position() -> Position:
        return Position.BottomLeft

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        self.is_user_modified = False
        bg_color = ThemeManager.theme["color_scale"]["outer"]
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        ctk.CTkFrame.__init__(self, parent, fg_color=fg_color, bg_color=bg_color)
        Observer.__init__(self, network)

        self.text_window = ctk.CTkTextbox(self, fg_color=fg_color, undo=True, wrap="word")
        self.text_window.insert(tk.END, network.information_text)
        self.text_window.pack(fill="both", expand=True, pady=3, padx=3)

        self.bind_text_listeners()

    def update_(self, updated_component):
        if self.is_user_modified:
            return
        if updated_component[1] == "information_text":
            self.text_window.delete(0.0, tk.END)
            self.text_window.insert(0.0, self.observed_subject.information_text)

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        super().destroy()

    def set_modified(self, is_modified_by_user=False):
        """
        Marks that the text has been modified by the user.

        :param is_modified_by_user: whether text has been modified
        """
        self.is_user_modified = is_modified_by_user

    def update_network_information(self):
        """
        Updates the network information text in the model.
        """
        self.set_modified(True)
        self.controller.model_facade.update_network_information(
            self.text_window.get(0.0, tk.END))
        self.set_modified()

    def bind_text_listeners(self):
        """
        Binds listeners to events on which the information text should be updated in the model.
        """
        update_keys = ["<FocusOut>", "<KeyRelease-Return>", "<KeyRelease-period>", "<KeyRelease-space>"]
        for key in update_keys:
            self.text_window.bind(key, lambda _: self.update_network_information())
