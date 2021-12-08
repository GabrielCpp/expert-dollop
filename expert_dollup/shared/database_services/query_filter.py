from pydantic import BaseModel


class QueryFilter(BaseModel):
    class Config:
        allow_mutation = False

    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        self.__dict__["_args"] = kwargs

    @property
    def args(self) -> dict:
        return self._args
