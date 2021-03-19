import os
import inspect
import importlib
from ariadne import make_executable_schema, load_schema_from_path
from .graphql_context import GraphqlContext


def get_types():
    types = []

    for module in os.listdir(os.path.dirname(__file__)):
        if module == "__init__.py" or module[-3:] != ".py":
            continue

        module_content = importlib.import_module("." + module[:-3], __name__)

        types.extend(
            [value for name, value in module_content.__dict__.items() if name == types]
        )

    return types


types = get_types()
type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
schema = make_executable_schema(type_defs, *types)