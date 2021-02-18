import pytest
from typing import TypeVar, Type, Callable, Any, List
from fastapi import Response
from functools import singledispatch
from injector import Injector
from expert_dollup.app.modules.projection import bind_mapper
from expert_dollup.shared.automapping import Mapper


@pytest.fixture
def map_dao_to_dto():
    injector = Injector([bind_mapper])
    mapper = injector.get(Mapper)

    @singledispatch
    def apply_map(daos, dao, domain, dto):
        raise ValueError(f"Unsupported type {type(daos)}")

    @apply_map.register(dict)
    def apply_map_dict(daos_dict: dict, dao, domain, dto):
        daos = list(daos_dict.values())
        domains = mapper.map_many(daos, domain, dao)
        dtos = mapper.map_many(domains, dto, domain)
        return {key: item for key, item in zip(daos_dict.keys(), dtos)}

    @apply_map.register(list)
    def apply_map_dict(daos: list, dao, domain, dto):
        domains = mapper.map_many(daos, domain, dao)
        dtos = mapper.map_many(domains, dto, domain)
        return dtos

    return apply_map


def normalize_request_results(dto_cls, key: str):
    def parse_dto(data: list):
        return sorted(
            [dto_cls(**item).dict() for item in data],
            key=lambda c: c[key],
        )

    return parse_dto


def normalize_dtos(dtos, key: str):
    return sorted([dto.dict() for dto in dtos], key=lambda c: c[key])


Dao = TypeVar("Dao")


def unwrap(response: Response, obj_type: Type):
    return obj_type(**response.json())


def unwrap_many(
    response: Response, dao: Type, sort_by_key: Callable[[Dao], Any]
) -> List[Dao]:
    return sorted([dao(**item) for item in response.json()], key=sort_by_key)