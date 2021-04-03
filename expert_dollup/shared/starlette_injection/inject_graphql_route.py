from inspect import signature, Parameter
from fastapi import params
from functools import wraps
from .inject_controller import Inject


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
