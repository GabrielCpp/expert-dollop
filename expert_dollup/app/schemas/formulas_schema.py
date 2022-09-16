from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.app.controllers.formulas_controller import (
    find_paginated_formulas,
    find_formula_by_id,
)
from .types import query


@query.field("findProjectDefinitionFormulas")
@inject_graphql_route(find_paginated_formulas, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_find_project_definition_formulas(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    query: str,
    first: int,
    find_paginated_formulas,
    after: Optional[str] = None,
):
    return await find_paginated_formulas(
        info, UUID(project_definition_id), first, after
    )


@query.field("findFormula")
@inject_graphql_route(find_formula_by_id, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_find_formula(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    formula_id: str,
    find_formula_by_id,
):
    return await find_formula_by_id(info, UUID(project_definition_id), UUID(formula_id))
