class QueryFilter:
    def __init__(self, **kwargs):
        self._args = kwargs

    @property
    def args(self) -> dict:
        return self._args
