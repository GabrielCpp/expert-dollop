from dataclasses import dataclass


@dataclass(init=False)
class QueryFilter:
    _args: dict

    def __init__(self, **kwargs):
        for name in self.__dataclass_fields__.keys():
            setattr(self, name, kwargs.get(name, None))

        self._args = kwargs

    def put(self, name: str, value):
        setattr(self, name, value)
        self._args[name] = value

    def put_when_present(self, name: str, value, blank=None):
        if not value is blank:
            setattr(self, name, value)
            self._args[name] = value

    @property
    def args(self) -> dict:
        assert not self._args is None
        return self._args

    def __eq__(self, other):
        if not issubclass(type(other), QueryFilter):
            return False

        return self._args == other._args
