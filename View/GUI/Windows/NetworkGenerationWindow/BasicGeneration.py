import tkinter as tk
from idlelib.tooltip import Hovertip

import PIL.Image
import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.CustomWidgets.ScrolledFrame import ScrolledFrame


class BasicGeneration(ScrolledFrame):
    def __init__(self, parent, controller, random_seed=None, min_node=100, max_node=120, min_edge=150,
                 max_edge=200, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller

        self.scrolled_frame.columnconfigure(0, weight=1)
        self.scrolled_frame.columnconfigure(1, weight=1)

        self.run_button_img = ctk.CTkImage(
            PIL.Image.open('View/GUI/images/run_button.png'), size=(50, 50))
        self.params = {
            "seed": random_seed,
            "min. number of nodes": min_node,
            "max. number of nodes": max_node,
            "min. number of edges": min_edge,
            "max. number of edges": max_edge,
        }
        self.entries = {}

        self.checkbox = ctk.CTkCheckBox(self.scrolled_frame, text="")
        self.add_entries()
        self.add_run_button(len(self.params) + 2)

    def add_entries(self):
        """
        Adds parameter entries to the widget.
        """
        index = 0
        for index, (name, value) in enumerate(self.params.items()):
            ctk.CTkLabel(self.scrolled_frame, text=name).grid(row=index, column=0, sticky="news", padx=5, pady=5)
            entry = ctk.CTkEntry(self.scrolled_frame)
            entry.insert(0, str(value))
            entry.grid(row=index, column=1, sticky="news", padx=5, pady=5)
            self.entries[name] = entry

        ctk.CTkLabel(self.scrolled_frame, text="remove single nodes") \
            .grid(row=index + 1, column=0, sticky="news", padx=5, pady=5)
        self.checkbox.grid(row=index + 1, column=1, sticky="news", padx=5, pady=5)
        self.checkbox.select()

    def update_entries(self):
        """
        Updates parameter values.
        """
        for name, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.params[name]))

    def add_run_button(self, index):
        """
        Adds a run button to the widget.

        :param index: row index
        """
        color = ThemeManager.theme["color_scale"]["inner_1"]
        bt = ctk.CTkButton(self.scrolled_frame, text=" ", width=10, image=self.run_button_img, fg_color=color,
                           command=self.run_generation)
        bt.grid(row=index, column=0, columnspan=2, padx=5, pady=5, sticky="news")
        Hovertip(bt, text="Generate network in new window", hover_delay=500)

    def run_generation(self):
        """
        Runs the network generation.
        """
        self.read_input()
        self.controller.generate_random_network(seed=self.params["seed"],
                                                min_num_nodes=self.params["min. number of nodes"],
                                                max_num_nodes=self.params["max. number of nodes"],
                                                min_num_edges=self.params["min. number of edges"],
                                                max_num_edges=self.params["max. number of edges"],
                                                delete_not_connected_nodes=self.checkbox.get() == 1)

    def read_input(self):
        """
        Reads and stores the parameter values.
        """
        for name in self.params.keys():
            value = self.entries[name].get()
            try:
                if name == "seed":
                    value = None if value.lower() in ["none", "n", ""] else int(value)
                else:
                    value = int(value)
                self.params[name] = value
            except ValueError as e:
                self.controller.model_facade.notify_error(e)

    def clone_to(self, new_window: 'BasicGeneration'):
        """
        Clones the basic generation window into another window.

        :param new_window: new window
        """
        self.read_input()
        new_window.params = self.params
        new_window.update_entries()
        if self.checkbox.get():
            new_window.checkbox.select()
        else:
            new_window.checkbox.deselect()
