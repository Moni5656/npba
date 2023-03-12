from tkinter import messagebox

import customtkinter as ctk

from Controller.GUI.GUIController import GUIController
from Model.ModelFacade import ModelFacade
from View import Observer
from View.GUI.BaseApplication.LayoutWindow import LayoutWindow
from View.GUI.BaseApplication.Menubar import Menubar
from utils.utils import OS


class GUI(ctk.CTkToplevel, Observer):

    def update_(self, updated_component):
        if updated_component[1] == "new_model":
            model_facade = updated_component[0]
            if OS.MacOS:
                self.wrapper.set_icon('View/GUI/images/question_mark.png')
            in_new_window = messagebox.askyesno(message="Do you want to open the project in a new window?",
                                                title="Open Project", icon="error")
            if OS.MacOS:
                self.wrapper.set_icon('View/GUI/images/icon.png')

            GUI(model_facade)
            if not in_new_window:
                self.destroy()
        elif updated_component[1] == "name":
            self.title(f"Network Performance Bounds Analyzer - {updated_component[0].name}")

    def __init__(self, model_facade: ModelFacade = None):
        if model_facade is None:
            model_facade = ModelFacade()

        super().__init__()
        Observer.__init__(self, model_facade.network)
        from View.GUI import GUIWrapper
        self.wrapper = GUIWrapper.current_gui_wrapper
        self.wrapper.add_gui(self)

        self.model = model_facade
        self.controller = GUIController(self.model)

        # initialize root window
        self.title(f"Network Performance Bounds Analyzer - {model_facade.network.name}")
        self.geometry("%ix%i" % (self.winfo_screenwidth() * 0.8, self.winfo_screenheight() * 0.8))
        self.option_add('*tearOff', False)

        # configure fullscreen
        self.is_fullscreen = False
        self.bind_listeners()

        # build GUI with separate components
        self.menubar = None
        self.layout = None
        self.init_view()

    def init_view(self):
        """
        Initializes the default layout.
        """
        self.menubar = Menubar(self, self.controller)
        self.configure(menu=self.menubar)

        self.layout = LayoutWindow(self, self.controller, self.model.network)
        self.layout.pack(fill='both', expand=1)
        self.layout.add_default_content()

    def destroy(self, override_save_message=False):
        if not override_save_message:
            save = messagebox.askyesnocancel(message="Do you want to save your project?")
            if save is None:
                return
            elif save and not self.menubar.export_network():
                return
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        super().destroy()
        self.wrapper.remove_gui(self)

    def restore_default_layout(self):
        """
        Destroys current layout and restores the default layout.
        """
        self.after(1, lambda: self.destroy(override_save_message=True))
        GUI(self.model)

    def bind_listeners(self):
        """
        Bind all required listeners to the main window.
        """
        self.bind("<F3>", lambda _: self.toggle_fullscreen())
        self.bind("<Escape>", lambda _: self.end_fullscreen())

    def toggle_fullscreen(self):
        """
        Toggles the fullscreen option depending on the current state.
        """
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def end_fullscreen(self):
        """
        Deactivates the fullscreen mode.
        """
        self.is_fullscreen = False
        self.attributes("-fullscreen", self.is_fullscreen)
        return "break"
