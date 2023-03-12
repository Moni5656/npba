import tkinter as tk
from enum import IntEnum
from idlelib.tooltip import Hovertip
from tkinter.colorchooser import askcolor
from typing import Optional

import PIL.Image
import customtkinter as ctk
from customtkinter import ThemeManager

from Model.Network.Edge import Edge
from Model.Network.Flow import Flow
from Model.Network.Node import Node
from View.GUI.CustomWidgets.CustomFrame import CustomFrame
from View.GUI.Windows.ParameterWindow.ComponentConfiguration.ConfigurationTreeView import ConfigurationTreeView


def open_color_picker() -> Optional[str]:
    colors = askcolor(title="Choose a Color")
    return colors[1]


class TkParameterSection(ctk.CTkFrame):
    class ParameterType(IntEnum):
        Network = 0
        Node = 1
        Edge = 2
        Flow = 3

    def __init__(self, root, controller, observed_subject, parameter_type: ParameterType, dictionary):
        self.root_window = root
        self.controller = controller
        self.observed_subject = observed_subject
        self.parameter_type = parameter_type
        if parameter_type == TkParameterSection.ParameterType.Network:
            self.title = "Default Network Parameters"
        if parameter_type == TkParameterSection.ParameterType.Node:
            self.title = "Node Parameters"
        if parameter_type == TkParameterSection.ParameterType.Edge:
            self.title = "Edge Parameters"
        if parameter_type == TkParameterSection.ParameterType.Flow:
            self.title = "Flow Parameters"
        self.dictionary = dictionary
        self.entries = {}
        self.color_picker_img = ctk.CTkImage(PIL.Image.open('View/GUI/images/color_picker.png'))

        self.light_color = ThemeManager.theme["color_scale"]["inner"]
        self.dark_color = ThemeManager.theme["color_scale"]["outer"]
        super().__init__(root, fg_color=self.dark_color, bg_color=self.light_color, border_width=2,
                         border_color=self.light_color)

        self.create_heading()
        self.create_parameter_section()
        self.configuration_section = None
        self.configuration_treeview = None
        self.create_configuration_section()
        if len(self.observed_subject.configurations) > 0:
            self.show_configuration_section()

    def update_values(self, dictionary):
        """
        Updates all the parameter values displayed in the entry field based on the dictionary.
        """
        self.dictionary = dictionary
        default_entry_color = ThemeManager.theme["CTkEntry"]["border_color"]
        for parameter in dictionary:
            entry = self.entries[parameter]
            if "node" in parameter or "ID" in parameter or "path" == parameter:
                entry.configure(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, dictionary[parameter])
            entry.configure(border_color=default_entry_color)
            if "node" in parameter or "ID" in parameter or "path" == parameter:
                entry.configure(state="readonly")

        self.hide_or_show_configurations()

    def add_configuration(self, configuration):
        """
        Adds a configuration to the parameter section.

        :param configuration: configuration object
        """
        self.configuration_treeview.add(configuration)
        self.hide_or_show_configurations()

    def remove_configuration(self, group_id):
        """
        Removes a configuration from the parameter section.

        :param group_id: group ID of the configuration
        """
        self.configuration_treeview.remove(group_id)
        self.hide_or_show_configurations()

    def hide_or_show_configurations(self):
        """
        Hides or shows the configuration section depending on the number of configurations.
        """
        if len(self.observed_subject.configurations) > 0:
            self.show_configuration_section()
        else:
            self.hide_configuration_section()

    def create_parameter_section(self):
        """
        Adds a parameter section to the root scrolled frame.
        """
        background = ThemeManager.theme["color_scale"]["outer"]
        entry_frame = CustomFrame(self, color=background)
        entry_frame.columnconfigure(0, weight=1)
        entry_frame.columnconfigure(1, weight=1)
        entry_frame.grid(column=0, row=1, sticky="ew", padx=5, pady=5)
        self.columnconfigure(0, weight=1)

        for index, parameter in enumerate(self.dictionary):
            entry_label = ctk.CTkLabel(entry_frame, text=parameter + ":")
            entry_label.grid(row=index, sticky="ew", padx=(5, 0))

            entry = ctk.CTkEntry(entry_frame)
            entry.insert(0, self.dictionary[parameter])
            if "color" in parameter:
                entry.grid(row=index, column=1, sticky="ew", padx=(0, 5), pady=(0, 10))
                self.add_color_picker(entry, index, parameter, entry_frame)
            else:
                entry.grid(row=index, column=1, sticky="ew", columnspan=2, padx=(0, 5), pady=(0, 10))
            if "node" in parameter or "ID" in parameter or "path" in parameter:
                entry.configure(state="readonly")
            self.entries[parameter] = entry

            value_setter = self.get_setter_for_parameter_type()
            self.bind_entry(value_setter, entry, parameter)

    def create_heading(self):
        """
        Creates a bar with the heading of the section and a delete button.
        """
        if self.parameter_type == TkParameterSection.ParameterType.Network:
            heading = ctk.CTkLabel(self, text=self.title, fg_color=self.light_color)
        else:
            heading = ctk.CTkFrame(self, fg_color=self.light_color, bg_color=self.light_color)

            title = ctk.CTkLabel(heading, text=self.title, anchor="e", fg_color=self.light_color)
            title.grid(column=0, row=0, sticky="ew", padx=5)
            heading.columnconfigure(0, weight=1)

            delete_button = ctk.CTkButton(heading, text="x", fg_color=self.light_color,
                                          command=lambda: self.delete(self.observed_subject), width=10)
            delete_button.grid(column=1, row=0, sticky="e", padx=5)
            heading.columnconfigure(1, weight=1)
            Hovertip(delete_button, text="Delete", hover_delay=500)
        heading.grid(column=0, row=0, sticky="ew", padx=6, pady=(6, 0))

    def add_color_picker(self, entry, index, parameter, frame):
        """
        Adds a color picker next to an entry.

        :param entry: entry object
        :param index: row index
        :param parameter: parameter name
        :param frame: parent widget to place the color picker in
        """

        def set_color(): self.change_entry_color(entry, parameter, self.observed_subject)

        bt = ctk.CTkButton(frame, text=" ", image=self.color_picker_img, fg_color=self.light_color,
                           hover_color=self.light_color,
                           command=lambda: self.controller.color_entry_on_error(entry, set_color), width=30, height=30)
        bt.grid(row=index, column=2, sticky="ew", padx=(0, 10), pady=(0, 10))

    def delete(self, component):
        """
        Deletes a network component (node, edge, or flow) from the model.

        :param component: network component object
        """
        if isinstance(component, (Node, Edge, Flow)):
            self.controller.delete_component(component)

    def bind_entry(self, function, entry, parameter):
        """
        Binds methods to the parameter entries.

        :param function: method setting the parameter value in the model
        :param entry: entry object
        :param parameter: parameter name
        """
        entry.bind("<Tab>",
                   lambda _: self.controller.color_entry_on_error(entry, lambda: function(entry, parameter)))
        entry.bind("<Return>",
                   lambda _: self.controller.color_entry_on_error(entry, lambda: function(entry, parameter)))
        entry.bind("<Escape>", lambda event: self.update_values(self.dictionary))
        entry.bind("<FocusOut>", lambda event: self.update_values(self.dictionary))
        entry.bind("<FocusIn>", lambda _: entry.select_range(0, tk.END))

    def get_setter_for_parameter_type(self):
        """
        Returns a setter for the parameter entries.

        :return: setter lambda function
        """
        if self.parameter_type == TkParameterSection.ParameterType.Network:
            return lambda entry, parameter: self.controller.update_parameter(entry.get(), parameter,
                                                                             self.observed_subject)
        elif self.parameter_type == TkParameterSection.ParameterType.Node:
            return lambda entry, parameter: self.controller.update_parameter(entry.get(), parameter,
                                                                             self.observed_subject)
        elif self.parameter_type == TkParameterSection.ParameterType.Edge:
            return lambda entry, parameter: self.controller.update_parameter(entry.get(), parameter,
                                                                             self.observed_subject)
        elif self.parameter_type == TkParameterSection.ParameterType.Flow:
            return lambda entry, parameter: self.controller.update_parameter(entry.get(), parameter,
                                                                             self.observed_subject)
        else:
            return lambda: (print("unknown parameter type"))

    def change_entry_color(self, entry, parameter, observed_subject):
        color = open_color_picker()
        if color is not None:
            entry.delete(0, tk.END)
            entry.insert(0, color)
            self.controller.update_parameter(entry.get(), parameter, observed_subject)

    def create_configuration_section(self):
        """
        Creates a configuration section containing parameters for each configuration.
        """
        self.configuration_section = frame = ctk.CTkFrame(self, fg_color=self.light_color)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        heading = ctk.CTkLabel(frame, text="Configurations", fg_color=self.light_color)
        heading.grid(column=0, row=0, sticky="ew", padx=4, pady=(3, 0))

        self.configuration_treeview = ConfigurationTreeView(frame, self.controller,
                                                            self.observed_subject.configurations.values())
        self.configuration_treeview.grid(column=0, row=1, sticky="ew", padx=5, pady=(0, 5))

    def hide_configuration_section(self):
        """
        Hides the configuration section.
        """
        self.configuration_section.grid_forget()

    def show_configuration_section(self):
        """
        Displays the configuration section.
        """
        self.configuration_section.grid(column=0, row=2, sticky="news", padx=10, pady=6)
