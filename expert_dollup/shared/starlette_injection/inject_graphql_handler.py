from functools import wraps


def inject_graphql_handler(handler_type):
    def decorate(fn):
        @wraps(fn)
        def add_handler(*args, **kwargs):
            kwargs["handler"] = args[1].context.container.get(handler_type)
            return fn(*args, **kwargs)

        return add_handler

    return decorate