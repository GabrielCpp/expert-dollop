from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.project.project import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query, mutation


@query.field("findProjects")
@inject_graphql_handler(GraphqlPageHandler[ProjectService, ProjectDetailsDto])
@convert_kwargs_to_snake_case
async def resolve_find_projects(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    handler: GraphqlPageHandler[ProjectService, ProjectDetailsDto],
    after: Optional[str] = None,
):
    result = await handler.find_all(first, after)
    return result