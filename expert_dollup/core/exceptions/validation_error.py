from typing import List, Tuple
from expert_dollup.shared.starlette_injection import DetailedError


class ValidationError(DetailedError):
    @staticmethod
    def for_field(path, error, **props):
        return ValidationError(path, error, **props)

    @staticmethod
    def generic(error, **props):
        return ValidationError("*", error, **props)

    def __init__(self, path, error, **props):
        props.update(dict(path=path, error=error))
        DetailedError.__init__(self, "Validation error", **props)
