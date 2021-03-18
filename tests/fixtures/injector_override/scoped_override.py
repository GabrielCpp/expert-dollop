from collections import defaultdict

container_override = defaultdict(set)


def override_service(binder_fn):
    def override(fn):
        container_override[fn].add(binder_fn)
        return fn

    return override


def get_overrides_for(fn):
    return container_override[fn]