import importlib
import pkgutil
from typing import Type

from .WindowInterface import WindowInterface
from ..BaseApplication.Position import Position

_available_application_windows = []


def add_window(window_class: Type[WindowInterface], title: str, position: Position):
    """
    Adds a new window class to the available window types.

    :param window_class: window class
    :param title: window title
    :param position: position in the layout
    """
    _available_application_windows.append((window_class, title, position))


def get_available_windows():
    """
    Returns a list of available window types.

    :return: a list of available windows
    """
    return _available_application_windows


for _, module_name, is_pkg in pkgutil.walk_packages(
        __path__, __name__ + '.'):
    if is_pkg:
        importlib.import_module(module_name)

for window in WindowInterface.__subclasses__():
    add_window(window, window.get_title(), window.get_start_position())
