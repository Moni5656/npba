import tkinter as tk
from idlelib.tooltip import Hovertip

import PIL.Image
import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.CustomWidgets.ScrolledFrame import ScrolledFrame


class FlowGeneration(ScrolledFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.run_button_img = ctk.CTkImage(
            PIL.Image.open('View/GUI/images/run_button.png'), size=(50, 50))

        self.scrolled_frame.columnconfigure(0, weight=1)
        self.scrolled_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(self.scrolled_frame, text="seed").grid(row=0, column=0, sticky="news", padx=5, pady=5)
        self.entry_flow_seed = ctk.CTkEntry(self.scrolled_frame)
        self.entry_flow_seed.grid(row=0, column=1, padx=5, pady=5, sticky="news")
        ctk.CTkLabel(self.scrolled_frame, text="min. number of flows").grid(row=1, column=0, sticky="news", padx=5,
                                                                            pady=5)
        self.entry_flow_min = ctk.CTkEntry(self.scrolled_frame)
        self.entry_flow_min.grid(row=1, column=1, padx=5, pady=5, sticky="news")
        ctk.CTkLabel(self.scrolled_frame, text="max. number of flows").grid(row=2, column=0, sticky="news", padx=5,
                                                                            pady=5)
        self.entry_flow_max = ctk.CTkEntry(self.scrolled_frame)
        self.entry_flow_max.grid(row=2, column=1, padx=5, pady=5, sticky="news")
        ctk.CTkLabel(self.scrolled_frame, text="min. number of nodes in flow path").grid(
            row=3, column=0, sticky="news", padx=5, pady=5)
        self.entry_flow_path_min = ctk.CTkEntry(self.scrolled_frame)
        self.entry_flow_path_min.grid(row=3, column=1, padx=5, pady=5, sticky="news")
        ctk.CTkLabel(self.scrolled_frame, text="max. number of nodes in flow path").grid(
            row=4, column=0, sticky="news", padx=5, pady=5)
        self.entry_flow_path_max = ctk.CTkEntry(self.scrolled_frame)
        self.entry_flow_path_max.grid(row=4, column=1, padx=5, pady=5, sticky="news")

        self._init_entry_values()

        light_color = ThemeManager.theme["color_scale"]["inner_1"]
        run_button = ctk.CTkButton(
            self.scrolled_frame, text=" ", width=10, image=self.run_button_img, fg_color=light_color,
            command=self.add_random_flows)
        run_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="news")
        Hovertip(run_button, text="Generate flows", hover_delay=500)

    def _init_entry_values(self):
        """
        Initializes start values for the entries.
        """
        self.entry_flow_seed.insert(0, "None")
        self.entry_flow_min.insert(0, 1)
        self.entry_flow_max.insert(0, 10)
        self.entry_flow_path_min.insert(0, 2)
        self.entry_flow_path_max.insert(0, 7)

    def add_random_flows(self):
        """
        Adds random flows to the model.
        """
        try:
            self.controller.model_facade.add_random_flows(
                min_num_flows=int(self.entry_flow_min.get()), max_num_flows=int(self.entry_flow_max.get()),
                min_num_nodes_in_flow_path=int(self.entry_flow_path_min.get()),
                max_num_nodes_in_flow_path=int(self.entry_flow_path_max.get()),
                flow_seed=None if self.entry_flow_seed.get().lower() in ("none", "")
                else int(self.entry_flow_seed.get()))
        except ValueError as e:
            self.controller.model_facade.notify_error(e)

    def clone_to(self, new_window: 'FlowGeneration'):
        """
        Clones the flow generation window to another window.

        :param new_window: new window
        """
        new_window.entry_flow_seed.delete(0, tk.END)
        new_window.entry_flow_seed.insert(0, self.entry_flow_seed.get())
        new_window.entry_flow_min.delete(0, tk.END)
        new_window.entry_flow_min.insert(0, self.entry_flow_min.get())
        new_window.entry_flow_max.delete(0, tk.END)
        new_window.entry_flow_max.insert(0, self.entry_flow_max.get())
        new_window.entry_flow_path_min.delete(0, tk.END)
        new_window.entry_flow_path_min.insert(0, self.entry_flow_path_min.get())
        new_window.entry_flow_path_max.delete(0, tk.END)
        new_window.entry_flow_path_max.insert(0, self.entry_flow_path_max.get())
