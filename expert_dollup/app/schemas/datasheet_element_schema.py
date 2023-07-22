from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.controllers.datasheet.datasheet_element_controller import *
from expert_dollup.app.dtos import *
from .types import datasheet_element


@datasheet_element.field("schema")
@inject_graphql_route(find_datasheet_by_id)
@convert_kwargs_to_snake_case
async def resolve_element_definition(
    parent: DatasheetElement, info: GraphQLResolveInfo, find_datasheet_element: callable
):
    datasheet_dto = await find_datasheet_by_id(info, parent.datasheet_id)
    schema_dto = datasheet_dto.instances_schema[parent.aggregate_id]
    return schema_dto
