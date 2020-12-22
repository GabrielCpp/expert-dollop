from typing import List, Tuple


class ValidationError(Exception):

    @staticmethod
    def for_field(name: str, message: str) -> "ValidationError":
        return ValidationError([(name, message)])

    def __init__(self, errors: List[Tuple[str, str]]):
        Exception.__init__(self, "Validation error")
        self.message = "Validation error"
        self.errors = errors
