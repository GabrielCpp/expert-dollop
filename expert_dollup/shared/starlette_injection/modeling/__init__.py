from pydantic import BaseModel
from pydantic.generics import GenericModel
from humps import camelize

# https://medium.com/analytics-vidhya/camel-case-models-with-fast-api-and-pydantic-5a8acb6c0eee


def to_camel(string):
    return camelize(string)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class GeneriCamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
