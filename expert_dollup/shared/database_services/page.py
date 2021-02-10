from dataclasses import dataclass
from typing import TypeVar, List, Generic, Optional

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    next_page_token: Optional[str]
    limit: int
    results: List[T]
