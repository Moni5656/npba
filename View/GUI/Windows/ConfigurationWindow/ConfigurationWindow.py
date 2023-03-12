import tkinter as tk
from idlelib.tooltip import Hovertip

import customtkinter as ctk
from customtkinter import ThemeManager

import Model
from Model.ComputationConfigurations.ConfigurationTemplate.AbstractNetworkConfiguration import \
    AbstractNetworkConfiguration
from View.GUI.BaseApplication.Position import Position
from View.GUI.CustomWidgets.CustomFrame import CustomFrame
from View.GUI.CustomWidgets.ScrolledFrame import ScrolledFrame
from View.GUI.Windows import WindowInterface
from View.GUI.Windows.ConfigurationWindow.CurrentConfiguration import CurrentConfiguration
from View.Observer import Observer


class ConfigurationWindow(WindowInterface, ScrolledFrame, Observer):

    @staticmethod
    def get_title() -> str:
        return "Configuration"

    @staticmethod
    def get_start_position() -> Position:
        return Position.BottomRight

    @staticmethod
    def get_importance():
        return 5

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        ScrolledFrame.__init__(self, parent)
        Observer.__init__(self, network)

        self.first_option_dropdown = None
        self.second_option_dropdown = None
        self.third_option_dropdown = None
        self.add_button = None
        self.information_section = CustomFrame(self.scrolled_frame)
        self.information_section.grid(column=0, row=2, columnspan=4, sticky="ews", pady=(25, 0))

        self.info_text_box = ctk.CTkTextbox(self.information_section, height=100, wrap="word")
        self.info_text_box.pack(side="left", fill="both", expand=True, pady=3, padx=3)
        self.current_configurations = {}

        self.light_color = ThemeManager.theme["color_scale"]["inner_1"]
        self.controller = controller
        self.add_first_option_selection()

        self.scrolled_frame.columnconfigure(0, weight=1)
        self.scrolled_frame.columnconfigure(1, weight=1)
        self.scrolled_frame.columnconfigure(2, weight=1)
        self.scrolled_frame.columnconfigure(3, weight=1)
        self.scrolled_frame.rowconfigure(0, weight=1)

        current_configurations = ctk.CTkLabel(self.scrolled_frame, text="Currently created configurations:")
        current_configurations.grid(column=0, row=3, columnspan=4, pady=(15, 0))
        self.current_configurations_frame = CustomFrame(self.scrolled_frame)
        self.current_configurations_frame.grid(column=0, row=4, columnspan=4, sticky="ew")
        self.load_initial_configurations()

    def load_initial_configurations(self):
        """
        Displays previously added configurations.
        """
        for configuration in self.observed_subject.configurations.values():
            self.add_current_configuration(configuration)

    def update_(self, updated_component):
        if isinstance(updated_component[0], AbstractNetworkConfiguration):
            if updated_component[1] == "add_configuration":
                self.add_current_configuration(updated_component[0])
                self.update_idletasks()
                self._resize_viewport(None)
        if updated_component[1] == "delete_configuration":
            self.current_configurations[updated_component[0]].destroy()
            del self.current_configurations[updated_component[0]]
            self.update_idletasks()
            self._resize_viewport(None)

    def update_information_section(self):
        """
        Updates the information text according to the currently selected configuration.
        """
        first = self.first_option_dropdown.get()
        second = self.second_option_dropdown.get()
        third = self.third_option_dropdown.get()
        description = Model.get_network_configuration_from_options(first, second, third) \
            .get_configuration_information()

        self.info_text_box.delete(0.0, tk.END)
        self.info_text_box.insert(0.0, description)

    def add_current_configuration(self, configuration: AbstractNetworkConfiguration):
        """
        Displays a given configuration in the application.

        :param configuration: configuration object
        """
        self.current_configurations[configuration.group_id] = config = CurrentConfiguration(
            self.current_configurations_frame, self.controller, configuration)
        config.pack(side="left", padx=3, pady=3)

    def add_first_option_selection(self):
        """
        Adds the drop-down menu for the first option.
        """
        available_first_options = self.get_first_options()

        description = ctk.CTkLabel(self.scrolled_frame, text="Add a calculation configuration:")
        description.grid(column=0, row=0, columnspan=4)

        self.first_option_dropdown = ctk.CTkOptionMenu(self.scrolled_frame,
                                                       values=available_first_options,
                                                       command=lambda _: self.update_second_option_selection(),
                                                       fg_color=self.light_color
                                                       )
        self.first_option_dropdown.grid(column=0, row=1)
        Hovertip(self.first_option_dropdown, text="Select a computation option", hover_delay=500)
        self.add_second_option_selection()

    def add_second_option_selection(self):
        """
        Adds the drop-down menu for the second option.
        """
        available_second_options = self.get_second_options()
        self.second_option_dropdown = ctk.CTkOptionMenu(self.scrolled_frame, values=available_second_options,
                                                        command=lambda c: self.update_third_option_selection(),
                                                        fg_color=self.light_color)
        self.second_option_dropdown.grid(column=1, row=1)
        Hovertip(self.second_option_dropdown, text="Select a computation option", hover_delay=500)
        self.add_third_option_selection()

    def update_second_option_selection(self):
        """
        Updates the options available in the second drop-down menu.
        """
        available_second_options = self.get_second_options()
        self.second_option_dropdown.configure(values=available_second_options)
        self.second_option_dropdown.set(available_second_options[0])
        self.update_third_option_selection()

    def add_third_option_selection(self):
        """
        Adds the drop-down menu for the third option.
        """
        available_third_options = self.get_third_options()
        self.third_option_dropdown = dropdown = ctk.CTkOptionMenu(self.scrolled_frame,
                                                                  values=available_third_options,
                                                                  fg_color=self.light_color
                                                                  )
        dropdown.grid(column=2, row=1)
        Hovertip(dropdown, text="Select a computation option", hover_delay=500)
        self.update_information_section()
        self.make_add_button()

    def update_third_option_selection(self):
        """
        Updates the options available in the third drop-down menu.
        """
        available_third_options = self.get_third_options()
        self.third_option_dropdown.configure(values=available_third_options)
        self.third_option_dropdown.set(available_third_options[0])
        self.update_information_section()

    def make_add_button(self):
        """
        Creates the add configuration button.
        """
        self.add_button = btn = ctk.CTkButton(self.scrolled_frame, text="Add Configuration", fg_color=self.light_color,
                                              command=self.add_configuration_callback)
        btn.grid(column=3, row=1)
        Hovertip(btn, text="Add the currently selected configuration to every component", hover_delay=500)

    def add_configuration_callback(self):
        """
        Adds the currently selected configuration to the model.
        """
        first_option = self.first_option_dropdown.get()
        second_option = self.second_option_dropdown.get()
        third_option = self.third_option_dropdown.get()
        self.controller.add_configuration(first_option, second_option, third_option)

    def destroy(self):
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        super().destroy()

    @staticmethod
    def get_first_options():
        """
        Returns available options for the first drop-down menu.

        :return: a list of sorted options
        """
        values = set()
        for first_option, _, _ in Model.get_available_network_configurations().keys():
            values.add(first_option)
        return sorted(values)

    def get_second_options(self):
        """
        Returns available options for the second drop-down menu.

        :return: a list of sorted options
        """
        if self.first_option_dropdown is None:
            return None

        choice = self.first_option_dropdown.get()
        values = set()
        for first_option, second_option, _ in Model.get_available_network_configurations().keys():
            if choice == first_option:
                values.add(second_option)
        return sorted(values)

    def get_third_options(self):
        """
        Returns available options for the third drop-down menu.

        :return: a list of sorted options
        """
        if self.second_option_dropdown is None:
            return None

        first_choice = self.first_option_dropdown.get()
        second_choice = self.second_option_dropdown.get()
        values = set()
        for first_option, second_option, third_option in Model.get_available_network_configurations().keys():
            if first_choice == first_option and second_choice == second_option:
                values.add(third_option)
        return sorted(values)
