from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query


@query.field("findProjectDefinitionFormulas")
@inject_graphql_handler(GraphqlPageHandler[FormulaService, FormulaExpressionDto])
@convert_kwargs_to_snake_case
async def resolve_find_project_definition_formulas(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    query: str,
    first: int,
    handler: GraphqlPageHandler[DatasheetDefinitionService, DatasheetDefinitionDto],
    after: Optional[str] = None,
):
    return await handler.handle(
        FormulaFilter(project_def_id=project_def_id), first, after
    )
