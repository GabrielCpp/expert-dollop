from json import dumps
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
from .types import (
    datasheet_definition,
    datasheet_definition_element,
    project_definition,
)


@inject_graphql_route(find_datasheet_definition_by_id)
@project_definition.field("datasheetDefinition")
@datasheet_definition_element.field("datasheetDefinition")
@convert_kwargs_to_snake_case
async def resolve_datasheet_definition(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
    find_datasheet_definition_by_id: callable,
):
    return await find_datasheet_definition_by_id(info, parent.datasheet_def_id)


@inject_graphql_route(find_datasheet_definition_elements)
@datasheet_definition.field("elementsDefinition")
@convert_kwargs_to_snake_case
async def resolve_elements_definition(
    parent: DatasheetDefinitionDto,
    info: GraphQLResolveInfo,
    find_datasheet_definition_elements: callable,
):
    return await find_datasheet_definition_elements(info, parent.id)


@datasheet_definition.field("elementPropertiesSchema")
def resolve_element_definition(
    parent: DatasheetDefinitionDto,
    _: GraphQLResolveInfo,
):
    return [
        {"name": name, "schema": dumps(schema)}
        for name, schema in parent.element_properties_schema
    ]
