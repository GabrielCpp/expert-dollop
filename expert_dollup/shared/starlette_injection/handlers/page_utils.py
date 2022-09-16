from typing import Type, TypeVar, List
from ..modeling import CamelModel


def make_page_model(results_type: Type) -> CamelModel:
    Result = TypeVar("Result", bound=results_type)

    class PageDto(CamelModel):
        next_page_token: str
        limit: int
        has_next_page: bool
        results: List[Result]

    return PageDto
