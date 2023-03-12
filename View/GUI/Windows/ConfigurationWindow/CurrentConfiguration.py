from idlelib.tooltip import Hovertip

import customtkinter as ctk
from customtkinter import ThemeManager

from Controller.GUI.GUIController import GUIController
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractNetworkConfiguration import \
    AbstractNetworkConfiguration
from View.Observer import Observer


class CurrentConfiguration(ctk.CTkFrame, Observer):

    def __init__(self, parent, controller: GUIController, configuration: AbstractNetworkConfiguration):
        self.controller = controller
        super().__init__(parent, fg_color=ThemeManager.theme["color_scale"]["inner"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        fg_color = ThemeManager.theme["color_scale"]["inner_1"]

        self.name_button = ctk.CTkButton(self, text=configuration.name + "       ", fg_color=fg_color,
                                         hover_color=fg_color)
        self.name_button.grid(column=0, row=0)

        close_button = ctk.CTkButton(self, text="x", fg_color=fg_color, bg_color=fg_color, width=10,
                                     command=lambda: parent.after(100, lambda: self.controller.delete_configuration(
                                         self.observed_subject)))
        close_button.grid(column=0, row=0, sticky="e", padx=(0, 5))
        Hovertip(close_button, text="Delete", hover_delay=500)
        Observer.__init__(self, configuration)

    def update_(self, updated_component):
        if updated_component[1] == "set_parameter":
            if updated_component[0].name != self.name_button.cget("text"):
                self.name_button.configure(text=updated_component[0].name + "       ")

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        super().destroy()
