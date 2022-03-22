from abc import ABC, abstractmethod
from typing import TypeVar
from dataclasses import dataclass
from expert_dollup.shared.database_services import DatabaseContext, WhereFilter, Plucker

T = TypeVar("T")


class Speficiation(ABC):
    @abstractmethod
    async def is_satisfied(candidate: T) -> bool:
        pass


class AndSpec(Speficiation):
    children: List[Speficiation]

    def __init__(children: List[Speficiation]):
        self.children = children

    async def is_satisfied(candidate: T) -> bool:
        return all(spec.is_satisfied(candidate) for spec in self.children)


class OrSpec(Speficiation):
    children: List[Speficiation]

    def __init__(children: List[Speficiation]):
        self.children = children

    def is_satisfied(candidate: T) -> bool:
        return any(spec.is_satisfied(candidate) for spec in self.children)


class DocumentIdExistsSpec(Speficiation):
    def __init__(db_context: DatabaseContext, domain_type: Type):
        self.repository = db_context.get_repository(domain_type)

    async def is_satisfied(candidate: UUID):
        return await self.repository.has(candidate)


class DocumentIdNotFoundSpec(Speficiation):
    def __init__(db_context: DatabaseContext, domain_type: Type):
        self.repository = db_context.get_repository(domain_type)

    async def is_satisfied(candidate: UUID):
        return not await self.repository.has(candidate)


class DocumentExistsSpec(Speficiation):
    def __init__(db_context: DatabaseContext, domain_type: Type):
        self.repository = db_context.get_repository(domain_type)

    async def is_satisfied(candidate: WhereFilter):
        return await self.repository.exists(candidate)


class DocumentIdsExistsSpec(Speficiation):
    def __init__(
        db_context: DatabaseContext,
        domain_type: Type,
        build_pluck_filter: Callable[[List[UUID]], QueryFilter],
    ):
        self.plucker = db_context.bind_query(Plucker[domain_type])
        self.build_pluck_filter = build_pluck_filter

    async def is_satisfied(candidate: Iterable[UUID]):
        return not await self.plucker.plucks(build_pluck_filter, candidate)


class ChecksSpec(Speficiation):
    def __init__(checks: Dict[str, Callable[[T], bool]]):
        self.checks = checks

    def is_satisfied(candidate: UUID):
        pass
