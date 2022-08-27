import pytest
from typing import TypeVar, Type, Callable, Any, List
from fastapi import Response
from functools import singledispatch
from injector import Injector
from expert_dollup.shared.automapping import Mapper
from pydantic import BaseModel
from dataclasses import dataclass


@pytest.fixture
def map_dao_to_dto(mapper):
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


def make_sorter(key: Callable[[BaseModel], Any], sublist=lambda x: x):
    def do_sort(dtos: List[BaseModel]) -> List[BaseModel]:
        sublist(dtos).sort(key=key)
        return dtos

    return do_sort
