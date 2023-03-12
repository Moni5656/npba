from Model import ModelFacade
from .GUI import GUI
from .GUIWrapper import GUIWrapper


def open_gui_wrapper():
    """
    Runs a new application.
    """
    if GUIWrapper.current_gui_wrapper is None:
        GUIWrapper().mainloop()


def open_model(model_facade: ModelFacade):
    """
    Runs an application with an existing model.
    WARNING: Tkinter is not threadsafe. Use the thread that calls this method for all further calls to the model.

    :param model_facade: the model
    """

    if GUIWrapper.current_gui_wrapper is None:
        GUIWrapper(model_facade).mainloop()
    else:
        GUIWrapper.current_gui_wrapper.request_new_gui(model_facade)
