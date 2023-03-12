import shutil
import sys
import traceback


class OS:
    Unknown = False
    Windows = False
    MacOS = False
    Linux = False

    left_mouse_button = "<1>"
    left_mouse_button_release = "<ButtonRelease-1>"
    left_mouse_button_motion = "<B1-Motion>"
    shift_left_mouse_button = "<Shift-Button-1>"
    right_mouse_button = "<3>"
    right_mouse_button_release = "<ButtonRelease-3>"
    right_mouse_button_motion = "<B3-Motion>"

    if sys.platform.startswith('win'):
        Windows = True
    elif sys.platform.startswith('linux'):
        Linux = True
    elif sys.platform.startswith('darwin'):
        MacOS = True
        right_mouse_button = "<2>"
        right_mouse_button_release = "<ButtonRelease-2>"
        right_mouse_button_motion = "<B2-Motion>"
    else:
        Unknown = True


def is_program_installed(program):
    """
    Checks whether a program is installed.

    :param program: program name
    :return: whether program is installed
    """
    is_available = shutil.which(program) is not None
    if not is_available:
        raise FileNotFoundError(f"{program} is not installed")
    return is_available


def print_exception_traceback(exception: Exception):
    """
    Prints the traceback of an exception.

    :param exception: exception
    """
    traceback.print_exception(type(exception), exception, exception.__traceback__)
