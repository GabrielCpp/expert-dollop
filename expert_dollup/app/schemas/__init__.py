import os
import inspect
import importlib
from .types import build_schema, GraphqlContext


def import_module_files():
    for module in os.listdir(os.path.dirname(__file__)):
        if module == "__init__.py" or module[-3:] != ".py":
            continue

        module_content = importlib.import_module("." + module[:-3], __name__)


import_module_files()
schema = build_schema()