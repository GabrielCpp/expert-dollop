from dataclasses import dataclass
from typing import Optional, TypeVar, Generic

Query = TypeVar("Query")


@dataclass
class PaginatedRessource(Generic[Query]):
    next_page_token: Optional[str]
    limit: int
    query: Query
