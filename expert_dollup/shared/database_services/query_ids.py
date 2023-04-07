from typing import Callable, Optional, TypeVar, Sequence, List
from uuid import UUID
from dataclasses import dataclass
from .adapter_interfaces import QueryFilter, Repository
from .query_builder import QueryBuilder
from .batch_helper import batch
from .query_reflector import queries


Domain = TypeVar("Domain")


@dataclass
class QuerySelfByPk:
    ids: list


@queries.register_executor(QuerySelfByPk)
async def quey_self_pk(
    repository: Repository[Domain], query: QuerySelfByPk
) -> List[Domain]:
    ressource_dict = {}
    primary_keys = repository.details.primary_keys

    if len(primary_keys) > 1:
        raise Exception("Self query will not work on composite key")

    name = primary_keys[0]
    query_builder = QueryBuilder()
    query_builder = query_builder.select(name).where(name, "in", query.ids)
    results = await repository.find_by(query_builder)

    return results
