from dataclasses import dataclass, field
from typing import TypeVar, List, Generic, Optional

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    limit: int = 500
    results: List[T] = field(default_factory=list)
    next_page_token: Optional[str] = None
    total_count: Optional[int] = None
