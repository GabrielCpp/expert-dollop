from dataclasses import dataclass


@dataclass(init=False)
class QueryFilter:
    _args: dict

    def __init__(self, **kwargs):
        for name in self.__dataclass_fields__.keys():
            setattr(self, name, kwargs.get(name, None))

        self._args = kwargs

    @property
    def args(self) -> dict:
        assert not self._args is None
        return self._args
