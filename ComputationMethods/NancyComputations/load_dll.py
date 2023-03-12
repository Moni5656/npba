import pythonnet as pynet
from clr_loader import get_coreclr

# initialize .NET core runtime
pynet.load(get_coreclr())

import clr


def load_dll(dll_dir, dll_name):
    """
    Loads .NET dll.

    :param dll_dir: directory of the dll file
    :param dll_name: name of the dll file
    """
    clr.AddReference(dll_dir + dll_name)
