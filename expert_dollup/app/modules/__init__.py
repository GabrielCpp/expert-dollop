import os
import inspect
import importlib
from injector import Injector, singleton, InstanceProvider


def build_container(root_binded=[]) -> Injector:
    binders = []

    for module in os.listdir(os.path.dirname(__file__)):
        if module == "__init__.py" or module[-3:] != ".py":
            continue

        module_content = importlib.import_module("." + module[:-3], __name__)

        binders.extend(
            [
                func
                for func_name, func in module_content.__dict__.items()
                if inspect.isfunction(func) and func_name.startswith("bind_")
            ]
        )

    injector = Injector([*binders, *root_binded])
    injector.binder.bind(Injector, to=InstanceProvider(injector), scope=singleton)

    return injector
