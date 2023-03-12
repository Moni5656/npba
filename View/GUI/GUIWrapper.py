import json
import os
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from customtkinter import ThemeManager

from Model.ModelFacade import ModelFacade
from View.GUI.GUI import GUI


class GUIWrapper(ctk.CTk):
    PATH_RECENT_FILE = "View/GUI/ConfigurationFiles/recently_used.json"
    PATH_CUSTOM_THEME = "View/GUI/ConfigurationFiles/custom_theme.json"
    NUM_OF_RECENT_FILES = 3
    EXAMPLE_PROJECTS_PATH = "ExampleProjects"

    current_gui_wrapper = None

    def __init__(self, model_facade=None):
        super().__init__()
        self._start_handler = None
        GUIWrapper.current_gui_wrapper = self

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme(self.PATH_CUSTOM_THEME)
        self.light_color = ThemeManager.theme["color_scale"]["inner"]
        self.dark_color = ThemeManager.theme["color_scale"]["outer"]
        self.configure(fg_color=self.light_color)
        self.is_visible = True
        self.guis = []

        self.title("Network Performance Bounds Analyzer")
        self.set_icon('View/GUI/images/icon.png')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        def make_new_gui(): GUI()

        b = ctk.CTkButton(self, fg_color=self.dark_color, text="New Project",
                          command=make_new_gui)
        b.grid(column=0, row=0, pady=(25, 0))
        b = ctk.CTkButton(self, fg_color=self.dark_color, text="Load Project",
                          command=self.open_project)
        b.grid(column=1, row=0, pady=(25, 0))
        self.recent_projects_frame = None
        self.make_recent_projects_section()
        self.examples_frame = None
        self.make_examples_section()

        self.requested_guis = []
        if model_facade is not None:
            self.requested_guis.append(model_facade)
        self._make_guis()

    def make_recent_projects_section(self):
        """
        Creates the recently used project section.
        """
        self.recent_projects_frame = ctk.CTkFrame(self, fg_color=self.dark_color)
        self.recent_projects_frame.grid(column=0, row=2, columnspan=2, sticky="news", padx=10, pady=(50, 0))
        heading = ctk.CTkLabel(self.recent_projects_frame, text="Recently Used Projects", fg_color=self.light_color)
        heading.pack(fill="x", padx=3, pady=3)

        for name, path in self.get_recent_projects():
            button = ctk.CTkButton(self.recent_projects_frame, fg_color=self.dark_color,
                                   text=f"{name}: {path}", command=self.make_open_file_lambda(path))
            button.pack(pady=5, padx=3, fill="x")

    def make_open_file_lambda(self, path):
        """
        Returns an open file lambda function.

        :param path: path to the file
        :return: lambda function
        """
        return lambda: self.open_project(path)

    def make_examples_section(self):
        """
        Creates the example projects section.
        """
        self.examples_frame = ctk.CTkFrame(self, fg_color=self.dark_color)
        self.examples_frame.grid(column=0, row=3, columnspan=2, sticky="news", padx=10, pady=(50, 25))
        heading = ctk.CTkLabel(self.examples_frame, text="Example Networks", fg_color=self.light_color)
        heading.pack(fill="x", padx=3, pady=3)

        files = self.get_example_files()
        for file in files:
            name_without_extension = os.path.splitext(file)[0]
            filepath = os.path.join(GUIWrapper.EXAMPLE_PROJECTS_PATH, file)
            button = ctk.CTkButton(self.examples_frame, fg_color=self.dark_color,
                                   text=name_without_extension,
                                   command=self.make_open_file_lambda(filepath))
            button.pack(pady=5, padx=3, fill="x")

    @staticmethod
    def get_example_files():
        """
        Returns a list of available example projects.

        :return: sorted list of example projects
        """
        files = []
        for file in os.listdir(GUIWrapper.EXAMPLE_PROJECTS_PATH):
            if os.path.isfile(os.path.join(GUIWrapper.EXAMPLE_PROJECTS_PATH, file)) and file.endswith(".json"):
                files.append(file)
        return sorted(files)

    def open_project(self, filepath=None) -> None:
        """
        Invokes a filedialog to import an existing network saved as json file.
        """
        if filepath is None:
            filepath = tk.filedialog.askopenfilename(title="Open Project",
                                                     filetypes=[("JavaScript Object Notation", "*.json")],
                                                     defaultextension=".json")
        if filepath != '':
            model = ModelFacade.load_network(filepath)
            self.save_to_recent(model.network.name, filepath)
            GUI(model)

    def set_icon(self, image_path):
        """
        Sets the application icon.

        :param image_path: path to the image
        """
        photo = tk.PhotoImage(file=image_path)
        self.wm_iconphoto(False, photo)

    def add_gui(self, gui: GUI):
        """
        Registers another GUI.

        :param gui: GUI object
        """
        self.guis.append(gui)
        self.hide()

    def remove_gui(self, gui: GUI):
        """
        Unregisters a GUI.

        :param gui: GUI object
        """
        self.guis.remove(gui)
        if len(self.guis) == 0:
            self.show()

    def show(self):
        """
        Displays the launcher.
        """
        self.recent_projects_frame.destroy()
        self.make_recent_projects_section()
        self.deiconify()

    def hide(self):
        """
        Hides the launcher.
        """
        self.iconify()

    @staticmethod
    def get_recent_projects():
        """
        Returns a list of recently used projects.

        :return: sorted list of recently used projects.
        """
        GUIWrapper.make_recent_file()
        with open(GUIWrapper.PATH_RECENT_FILE) as file:
            content = json.load(file)
        files = []
        for index, dictionary in enumerate(content):
            if index >= GUIWrapper.NUM_OF_RECENT_FILES:
                break
            files.append((dictionary["name"], dictionary["path"]))
        return files

    @staticmethod
    def save_to_recent(name, path):
        """
        Saves a project to the list of recently used projects.

        :param name: project name
        :param path: project path
        """
        GUIWrapper.make_recent_file()
        current = {"name": name, "path": path}
        with open(GUIWrapper.PATH_RECENT_FILE) as file:
            content_list = json.load(file)
        if isinstance(content_list, list) and current in content_list:
            content_list.remove(current)

        current = [current]
        for index, content in enumerate(content_list):
            if index + 1 >= GUIWrapper.NUM_OF_RECENT_FILES:
                break
            current.append(content)

        with open(GUIWrapper.PATH_RECENT_FILE, 'w') as file:
            file.write(json.dumps(current))

    @staticmethod
    def make_recent_file():
        """
        Creates a file to store recently used projects.
        """
        recent_file = Path(GUIWrapper.PATH_RECENT_FILE)
        if recent_file.exists():
            return
        with open(GUIWrapper.PATH_RECENT_FILE, 'w+') as file:
            file.write(json.dumps({}))

    def start_handler(self):
        """
        Starts a task handler.
        """
        self._start_handler = self.after(1000, self._make_guis)

    def _make_guis(self):
        """
        Handles requested GUIs.
        """
        for model in self.requested_guis:
            GUI(model)
        self.requested_guis.clear()
        self.start_handler()

    def request_new_gui(self, model_facade=None):
        """
        Requests a new GUI.

        :param model_facade: model
        """
        if model_facade is None:
            model_facade = ModelFacade()
        self.requested_guis.append(model_facade)

    def destroy(self):
        if GUIWrapper.current_gui_wrapper == self:
            GUIWrapper.current_gui_wrapper = None
        self.after_cancel(self._start_handler)
        super().destroy()
