import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

import View.GUI.Windows
from Controller.GUI.GUIController import GUIController
from Model.GraphLayoutAlgorithm import GraphLayoutAlgorithm as GraphLayouts
from View.GUI.CustomWidgets.CustomMenubar import CustomMenubar


class Menubar(CustomMenubar):

    def __init__(self, gui, controller: GUIController):
        super().__init__(gui)

        self.controller = controller
        self.gui = gui

        self.menu_file = CustomMenubar(self)
        self.menu_view = CustomMenubar(self)
        self.menu_help = CustomMenubar(self)
        self.menu_add_window = CustomMenubar(self.menu_view)
        self.appearance_mode_menu = CustomMenubar(self.menu_view)
        self.graph_layout = CustomMenubar(self.menu_view)

        self.add_cascades()
        self.add_commands()

    def add_cascades(self) -> None:
        """
        Adds all menu cascades.
        """
        self.add_cascade(menu=self.menu_file, label='File')
        self.add_cascade(menu=self.menu_view, label='View')
        self.add_cascade(menu=self.menu_help, label='Help')
        self.menu_view.add_cascade(menu=self.menu_add_window, label="Add Window")
        self.menu_view.add_cascade(menu=self.appearance_mode_menu, label="Change Appearance Mode")
        self.menu_view.add_cascade(menu=self.graph_layout, label="Change Graph Layout")

    def add_commands(self) -> None:
        """
        Adds all commands.
        """
        from View.GUI.GUI import GUI
        available_commands = [('New Project', lambda: GUI()),
                              ('Open Project in New Window',
                               lambda: GUI(self.gui.model)),
                              ('Import', self.import_network), ('Export', self.export_network),
                              ('Close Project', self.gui.destroy)]
        for label, command in available_commands:
            self.menu_file.add_command(label=label, command=command)

        available_windows = View.GUI.Windows.get_available_windows()
        available_windows.sort(key=lambda entry: entry[1])
        for window_class, title, position in available_windows:
            try:
                self.menu_add_window.add_command(
                    label=title, command=self.make_add_window_lambda(window_class, title, position))
            except Exception as e:
                self.controller.model_facade.notify_error(e)

        available_appearance_modes = [('Light', lambda: ctk.set_appearance_mode("light")),
                                      ('Dark', lambda: ctk.set_appearance_mode("dark")),
                                      ('System', lambda: ctk.set_appearance_mode("system"))]
        for label, command in available_appearance_modes:
            self.appearance_mode_menu.add_command(label=label, command=command)

        self.menu_view.add_command(label='Default Layout', command=self.gui.restore_default_layout)

        layouts = {}
        for enum in GraphLayouts:
            layouts[str(enum.value)] = enum
        names = sorted(layouts.keys())
        for name in names:
            self.graph_layout.add_command(
                label=name, command=self.make_change_graph_layout_lambda(layouts[name]))

    def export_network(self) -> bool:
        """
        Exports current network as JSON file by invoking a filedialog.
        """
        filename = tk.filedialog.asksaveasfilename(title="Save Project",
                                                   initialfile=self.controller.model_facade.network.name,
                                                   filetypes=[("JavaScript Object Notation", "*.json")],
                                                   defaultextension=".json")
        if filename == "":
            return False
        self.controller.export_network(filename)
        return True

    def import_network(self) -> None:
        """
        Invokes a filedialog to import an existing network, saved as JSON file.
        """
        file_path = tk.filedialog.askopenfilename(title="Open Project",
                                                  filetypes=[("JavaScript Object Notation", "*.json")],
                                                  defaultextension=".json")
        if file_path != '':
            self.controller.import_network(file_path)

    def make_add_window_lambda(self, window_class, title, position):
        """
        Creates a lambda function to add windows.

        :param window_class: class of the window
        :param title: name of the window
        :param position: position of the added window in the layout
        """

        def add_window_to_gui():
            window = window_class(
                parent=self.gui.layout.get_container_parent_at(position), controller=self.controller,
                network=self.gui.model.network)
            self.gui.layout.add_content(position, window, title)

        return lambda: add_window_to_gui()

    def make_change_graph_layout_lambda(self, layout):
        """
        Creates a lambda function to change the graph layout.

        :param layout: layout type
        :return: lambda function
        """
        return lambda: self.controller.model_facade.change_graph_layout(layout)
