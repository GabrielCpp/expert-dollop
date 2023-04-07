from typing import Callable, Optional, TypeVar, Sequence, List
from uuid import UUID
from dataclasses import dataclass
from .adapter_interfaces import QueryFilter, Repository
from .query_builder import QueryBuilder
from .batch_helper import batch
from .query_reflector import queries

Domain = TypeVar("Domain")


@dataclass
class Pluck:
    name: str
    ids: list


@dataclass
class PluckSubRessource:
    base: dict
    name: str
    ids: list


async def pluck_by_batch(
    repository: Repository[Domain],
    name: str,
    ids: List[UUID],
    base: Optional[dict] = None,
):
    ressource_dict = {}

    for ids_batch in batch(ids, repository.batch_size):
        query_builder = QueryBuilder()

        if not base is None:
            for column_name, value in base.items():
                query_builder = query_builder.where(column_name, "==", value)

        query_builder = query_builder.where(name, "in", ids)

        results = await repository.find_by(query_builder)
        yield results


@queries.register_executor(Pluck)
async def plucks(repository: Repository[Domain], query: Pluck) -> List[Domain]:
    all_results = []

    async for batch_results in pluck_by_batch(repository, query.name, query.ids):
        all_results.extend(batch_results)

    return all_results


@queries.register_executor(PluckSubRessource)
async def pluck_subressources(
    repository: Repository[Domain], query: PluckSubRessource
) -> List[Domain]:
    all_results = []

    async for batch_results in pluck_by_batch(
        repository, query.name, query.ids, query.base
    ):
        all_results.extend(batch_results)

    return all_results
