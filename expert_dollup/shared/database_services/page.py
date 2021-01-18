from dataclasses import dataclass
from typing import TypeVar, List, Generic

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    next_page_token: str
    limit: int
    results: List[T]