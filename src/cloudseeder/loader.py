"""
Implements logic for loading custom resource classes from `cloudseeder.resources`.
"""

import importlib
import inspect
import pkgutil

from . import resources


def get_classes_from_module(module):
    """
    Yields directly defined classes (not aliased) from a module.
    """
    for name in dir(module):
        value = getattr(module, name)
        if not inspect.isclass(value):
            continue
        if value.__module__ != module.__name__:
            continue
        yield value

def load_custom_resources(parent_module=None):
    """
    Yields all subclasses of `cloudseeder.resources.Resource` found under the `parent_module`.
    """
    if parent_module is None:
        parent_module = resources
    for _, name, _ in pkgutil.walk_packages(parent_module.__path__, parent_module.__name__ + '.'):
        module = importlib.import_module(name)
        for obj in get_classes_from_module(module):
            if issubclass(obj, resources.Resource) and obj != resources.Resource:
                yield obj
