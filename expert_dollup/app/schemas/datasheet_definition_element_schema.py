from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case, UnionType
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlPageHandler
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
from .types import datasheet_definition_element, query


@datasheet_definition_element.field("defaultProperties")
@convert_kwargs_to_snake_case
def resolve_default_properties(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
):
    return [
        {"name": name, "property": property_value}
        for name, property_value in parent.default_properties.items()
    ]


@query.field("findDatasheetDefinitionElements")
@inject_graphql_handler(GraphqlPageHandler[DatasheetDefinitionElement])
@convert_kwargs_to_snake_case
async def resolve_find_datasheet_definition_elements(
    _: Any,
    info: GraphQLResolveInfo,
    datasheet_definition_id: str,
    first: int,
    handler: GraphqlPageHandler[DatasheetDefinition],
    after: Optional[str] = None,
):
    return await handler.handle(
        DatasheetDefinitionElementDto,
        DatasheetDefinitionElementFilter(
            datasheet_def_id=UUID(datasheet_definition_id)
        ),
        first,
        after,
    )


@query.field("queryDatasheetDefinitionElements")
@inject_graphql_handler(GraphqlPageHandler[DatasheetDefinitionElement])
@convert_kwargs_to_snake_case
async def resolve_query_datasheet_definition_elements(
    _: Any,
    info: GraphQLResolveInfo,
    datasheet_definition_id: UUID,
    query: str,
    first: int,
    handler: GraphqlPageHandler[DatasheetDefinition],
    after: Optional[str] = None,
):

    return await handler.find_all(
        DatasheetDefinitionElementDto,
        first,
        after,
    )
