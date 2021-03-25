import os
import inspect
import importlib
from ariadne import make_executable_schema, load_schema_from_path
from expert_dollup.shared.starlette_injection import GraphqlContext
from .types import types


def import_module_files():
    for module in os.listdir(os.path.dirname(__file__)):
        if module == "__init__.py" or module[-3:] != ".py":
            continue

        module_content = importlib.import_module("." + module[:-3], __name__)


import_module_files()
type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
schema = make_executable_schema(type_defs, *types)