from abc import ABC, abstractmethod
from typing import TypeVar, Optional, List
from uuid import UUID
from dataclasses import dataclass, field
from expert_dollup.shared.database_services import Page
from .adapter_interfaces import Paginator
from .query_filter import QueryFilter

Domain = TypeVar("Domain")


@dataclass
class UserRessourceQuery:
    organization_id: UUID
    names: List[str] = field(default_factory=list)


class UserRessourcePaginator(Paginator[Domain]):
    @abstractmethod
    async def find_page(
        self,
        query: UserRessourceQuery,
        limit: int,
        next_page_token: Optional[str],
    ) -> Page[Domain]:
        pass

    @abstractmethod
    def make_record_token(self, domain: Domain) -> str:
        pass
