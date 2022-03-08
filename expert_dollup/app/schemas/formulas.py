from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import Paginator
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
    AuthService,
    GraphqlPageHandler,
)
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query


@query.field("findProjectDefinitionFormulas")
@inject_graphql_handler(GraphqlPageHandler[Paginator[Formula]])
@convert_kwargs_to_snake_case
async def resolve_find_project_definition_formulas(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: str,
    query: str,
    first: int,
    handler: GraphqlPageHandler[Paginator[Formula]],
    after: Optional[str] = None,
):
    user = await info.context.container.get(AuthService).can_perform_required(
        info.context.request,
        ["formula:read"],
    )

    return await handler.handle(
        FormulaExpressionDto,
        FormulaFilter(project_def_id=UUID(project_def_id)),
        first,
        after,
    )
