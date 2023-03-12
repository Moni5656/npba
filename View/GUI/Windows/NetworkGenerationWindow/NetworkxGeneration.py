import inspect
import tkinter as tk
from idlelib.tooltip import Hovertip

import PIL.Image
import customtkinter as ctk
from customtkinter import ThemeManager

import Model
from View.GUI.CustomWidgets.CustomFrame import CustomFrame
from View.GUI.CustomWidgets.ScrolledFrame import ScrolledFrame


class NetworkxGeneration(ScrolledFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.run_button_img = ctk.CTkImage(
            PIL.Image.open('View/GUI/images/run_button.png'), size=(50, 50))

        self.scrolled_frame.columnconfigure(0, weight=1)

        light_color = ThemeManager.theme["color_scale"]["inner_1"]
        self.function_dropdown = ctk.CTkOptionMenu(
            self.scrolled_frame, command=self.update_arguments_and_documentation, fg_color=light_color)
        self.function_dropdown.grid(row=0, column=0, padx=5, pady=5, sticky="news")

        self.args_frame = CustomFrame(self.scrolled_frame)
        self.args_frame.columnconfigure(0, weight=1)
        self.args_frame.columnconfigure(1, weight=1)
        self.args_frame.grid(row=1, column=0, padx=5, pady=5, sticky="news")

        self.function_documentation = ctk.CTkTextbox(self.scrolled_frame, height=300, wrap="word")
        self.function_documentation.grid(row=2, column=0, padx=5, pady=5, sticky="news")
        self.function_documentation.insert(0., "Function Documentation here")

        run_button = ctk.CTkButton(
            self.scrolled_frame, text=" ", width=10, image=self.run_button_img, fg_color=light_color,
            command=self.run_generator_with_args)
        run_button.grid(row=3, column=0, padx=5, pady=5, sticky="news")
        Hovertip(run_button, text="Generate network in new window", hover_delay=500)

        self.generator_functions = {}
        self._load_generator_functions()
        self._argument_labels_entries = {}
        self.update_arguments_and_documentation(self.function_dropdown.get())

    def _load_generator_functions(self):
        """
        Loads available NetworkX generation methods into the drop-down menu.
        """
        try:
            for (name, fun) in Model.get_networkx_generator_functions():
                self.generator_functions[name] = (fun, inspect.signature(fun))
        except Exception as e:
            self.controller.model_facade.notify_error(e)
            raise e
        values = sorted(self.generator_functions.keys())
        self.function_dropdown.configure(values=values)
        self.function_dropdown.set(values[0])

    def _get_generator_arguments(self):
        """
        Reads entry values to pass them as arguments to the NetworkX method.

        :return: dictionary of arguments
        """
        arg_string = ""
        for arg_name, (_, entry) in self._argument_labels_entries.items():
            arg_value = entry.get().replace(" ", "")
            if arg_value == "":
                continue
            arg_string += f"{arg_name}={arg_value},"
        arg_string = arg_string.replace("\n", "").replace("\r", "")

        try:
            kwargs = eval(f"dict({arg_string})")
        except Exception as e:
            self.controller.model_facade.notify_error(e)
            raise Exception("Can not proceed without arguments")
        return kwargs

    def update_arguments_and_documentation(self, method_name):
        """
        Updates the argument entries and the documentation text according to the currently selected option of the
        drop-down menu.

        :param method_name: NetworkX network generation method
        """
        self._delete_arguments()

        fun, signature = self.generator_functions[method_name]
        for index, arg_name in enumerate(signature.parameters):
            arg_name = str(arg_name)
            label = ctk.CTkLabel(self.args_frame, text=arg_name)
            label.grid(row=index, column=0, padx=5, pady=5, sticky="news")
            entry = ctk.CTkEntry(self.args_frame)
            entry.grid(row=index, column=1, padx=5, pady=5, sticky="news")
            self._argument_labels_entries[arg_name] = label, entry

        documentation = f"Parameters: {signature}\n\n{inspect.getdoc(fun)}"
        self.function_documentation.configure(state=tk.NORMAL)
        self.function_documentation.delete(0., tk.END)
        self.function_documentation.insert(0., documentation)
        self.function_documentation.configure(state=tk.DISABLED)

    def _delete_arguments(self):
        """
        Destroys all argument entries.
        """
        for label, entry in self._argument_labels_entries.values():
            label.destroy()
            entry.destroy()
        self._argument_labels_entries.clear()

    def run_generator_with_args(self):
        """
        Runs the generator with the given argument values.
        """
        fun = self.generator_functions[self.function_dropdown.get()][0]
        kwargs = self._get_generator_arguments()
        self.controller.model_facade.generate_networkx_network_in_new_model(generator=fun, **kwargs)

    def clone_to(self, new_window: 'NetworkxGeneration'):
        """
        Clones the network generation window to another window.

        :param new_window: new window
        """
        new_window.function_dropdown.set(self.function_dropdown.get())
        new_window.update_arguments_and_documentation(new_window.function_dropdown.get())
        for arg_name, (_, entry) in self._argument_labels_entries.items():
            if arg_name in new_window._argument_labels_entries:
                _, other_entry = new_window._argument_labels_entries[arg_name]
                other_entry.insert(0, entry.get())
