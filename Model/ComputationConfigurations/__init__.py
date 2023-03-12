import importlib
import pkgutil

for _, module_name, is_pkg in pkgutil.walk_packages(
        __path__, __name__ + '.'):
    if is_pkg:
        importlib.import_module(module_name)
