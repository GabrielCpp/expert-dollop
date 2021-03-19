from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case, UnionType
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_element_controller import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_controller import *

datasheet_definition_element = ObjectType("DatasheetDefinitionElement")


@inject_graphql_route(find_datasheet_definition_by_id)
@datasheet_definition_element.field("datasheetDefinition")
@convert_kwargs_to_snake_case
async def resolve_element_definition(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
    find_datasheet_definition_by_id: callable,
):
    return await find_datasheet_definition_by_id(info, parent.datasheet_def_id)


@datasheet_definition_element.field("defaultProperties")
@convert_kwargs_to_snake_case
def resolve_default_properties(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
):
    return [
        {"name": name, "property": str(property_value)}
        for name, property_value in parent.default_properties.items()
    ]


types = [datasheet_definition_element]