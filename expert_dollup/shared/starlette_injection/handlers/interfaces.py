from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from dataclasses import dataclass
from ...database_services import Paginator, QueryFilter

Domain = TypeVar("Domain")


@dataclass
class MappingChain:
    dto: Optional[Type] = None
    domain: Optional[Type] = None
    out_domain: Optional[Type] = None
    out_dto: Optional[Type] = None
    value: Optional[Any] = None


class PageHandler(ABC):
    @abstractmethod
    def use_paginator(self, paginator: Paginator[Domain]) -> "PageHandler":
        pass

    @abstractmethod
    async def handle(
        self,
        out_dto: Type[BaseModel],
        query: QueryFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ):
        pass
