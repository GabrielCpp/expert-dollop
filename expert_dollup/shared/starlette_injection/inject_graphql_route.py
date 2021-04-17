from inspect import signature, Parameter
from typing import Dict, List
from fastapi import params
from functools import wraps
from .inject_controller import Inject


def collapse_union(node: dict, path: List[str], kind_map: Dict[str, str]):
    assert len(path) > 0

    last_target_node = node
    target_node = node

    for property_name in path:
        if not isinstance(target_node, dict):
            return node

        last_target_node = target_node
        target_node = target_node.get(property_name)

    if target_node["kind"] in kind_map:
        target_property_name = kind_map[target_node["kind"]]
        union_value = target_node[target_property_name]
        last_target_node[path[-1]] = union_value
    else:
        kind = target_node["kind"]
        raise KeyError(f"Missing type {kind}")

    return node


def inject_graphql_route(fn):
    sig = signature(fn)
    injectables = {}

    for parameter in sig.parameters.values():
        if (
            parameter.default is not Parameter.empty
            and isinstance(parameter.default, params.Depends)
            and isinstance(parameter.default.dependency, Inject)
        ):
            injectables[parameter.name] = parameter.default.dependency

    def invoke(info, *args, **kwargs):
        for (name, dependency) in injectables.items():
            kwargs[name] = dependency(info.context.request)

        return fn(*args, **kwargs)

    def decorator(decorated_fn):
        @wraps(decorated_fn)
        def with_injection(*args, **kwargs):
            kwargs[fn.__name__] = invoke
            return decorated_fn(*args, **kwargs)

        return with_injection

    return decorator
