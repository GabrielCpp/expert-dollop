from typing import Generic, TypeVar, List, Optional
from expert_dollup.shared.starlette_injection import GeneriCamelModel

DataT = TypeVar("DataT")


class PageDto(GeneriCamelModel, Generic[DataT]):
    limit: int
    results: List[DataT]
    next_page_token: Optional[str]
    total_count: Optional[int]


def bind_page_dto(m):
    class BindedPageDto(GeneriCamelModel, Generic[DataT]):
        limit: int
        results: List[m]
        next_page_token: Optional[str]
        total_count: Optional[int]

    return BindedPageDto
