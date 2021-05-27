from json import dumps
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
    datasheet_definition_property_schema_dict,
    datasheet_definition,
    datasheet_definition_element,
    project_definition,
    query,
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


@datasheet_definition_property_schema_dict.field("schema")
def resolve_element_definition(
    parent: ElementPropertySchemaDto,
    _: GraphQLResolveInfo,
):
    return dumps(parent.valueValidator)


@datasheet_definition.field("properties")
def resolve_element_definition(
    parent: DatasheetDefinitionDto,
    _: GraphQLResolveInfo,
):
    return [
        {"name": name, "schema": schema.dict()}
        for name, schema in parent.properties.items()
    ]


@query.field("findDatasheetDefinitions")
@inject_graphql_handler(
    GraphqlPageHandler[DatasheetDefinitionService, DatasheetDefinitionDto]
)
@convert_kwargs_to_snake_case
async def resolve_find_datasheet_definitions(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    handler: GraphqlPageHandler[DatasheetDefinitionService, DatasheetDefinitionDto],
    after: Optional[str] = None,
):
    return await handler.find_all(first, after)


@query.field("findDatasheetDefinition")
@inject_graphql_route(find_datasheet_definition_by_id)
@convert_kwargs_to_snake_case
async def resolve_find_datasheet_definitions(
    _: Any,
    info: GraphQLResolveInfo,
    datasheet_definition_id: UUID,
    find_datasheet_definition_by_id: callable,
):
    return await find_datasheet_definition_by_id(info, datasheet_definition_id)
