from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_element_controller import *
from .types import datasheet_element


@inject_graphql_route(find_datasheet_element)
@datasheet_element.field("elementDefinition")
@convert_kwargs_to_snake_case
async def resolve_element_definition(
    parent: DatasheetElement, info: GraphQLResolveInfo, find_datasheet_element: callable
):
    return await find_datasheet_element(
        info, parent.datasheet_id, parent.element_def_id, parent.child_element_reference
    )
