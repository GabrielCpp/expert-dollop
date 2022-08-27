from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case, UnionType
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import UserRessourceQuery, Paginator
from expert_dollup.shared.starlette_injection import (
    GraphqlPageHandler,
    inject_graphql_route,
    inject_graphql_handler,
    AuthService,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_element_controller import *
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
@inject_graphql_handler(GraphqlPageHandler[Paginator[DatasheetDefinitionElement]])
@convert_kwargs_to_snake_case
async def resolve_find_datasheet_definition_elements(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    first: int,
    handler: GraphqlPageHandler[Paginator[DatasheetDefinitionElement]],
    after: Optional[str] = None,
):
    await info.context.container.get(AuthService).can_perform_on_required(
        info.context.request,
        UUID(project_definition_id),
        ["project_definition:get"],
    )

    return await handler.handle(
        DatasheetDefinitionElementDto,
        DatasheetDefinitionElementFilter(
            project_definition_id=UUID(project_definition_id)
        ),
        first,
        after,
    )


@query.field("queryDatasheetDefinitionElements")
@inject_graphql_handler(GraphqlPageHandler[Paginator[DatasheetDefinitionElement]])
@convert_kwargs_to_snake_case
async def resolve_query_datasheet_definition_elements(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    query: str,
    first: int,
    handler: GraphqlPageHandler[Paginator[DatasheetDefinitionElement]],
    after: Optional[str] = None,
):
    await info.context.container.get(AuthService).can_perform_on_required(
        info.context.request,
        UUID(project_definition_id),
        ["project_definition:get"],
    )

    return await handler.handle(
        DatasheetDefinitionElementDto,
        DatasheetDefinitionElementFilter(
            project_definition_id=UUID(project_definition_id)
        ),
        first,
        after,
    )
