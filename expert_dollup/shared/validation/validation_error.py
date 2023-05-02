from typing import List
from .schema_core import ErrorMessage


class ValidationError(Exception):
    def __init__(self, errors: List[ErrorMessage]):
        Exception.__init__(self, f"validation_error: {errors}")
        self.errors = errors

    @property
    def message(self):
        return str(self)
