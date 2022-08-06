from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from uuid import UUID
from dataclasses import dataclass
from expert_dollup.shared.database_services import Page
from .query_filter import QueryFilter

Domain = TypeVar("Domain")


@dataclass
class UserRessourceQuery:
    organization_id: UUID
    names: Optional[List[str]] = None


class UserRessourcePaginator(Generic[Domain]):
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
