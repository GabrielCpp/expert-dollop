from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case, UnionType
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_element_controller import *
from .types import datasheet_definition_element, query


@query.field("findDatasheetDefinitionElements")
@inject_graphql_route(find_paginated_datasheet_elements, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_find_datasheet_definition_elements(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    query: str,
    first: int,
    find_paginated_datasheet_elements,
    after: Optional[str] = None,
):
    return await find_paginated_datasheet_elements(
        info,
        UUID(project_definition_id),
        first,
        after,
    )
