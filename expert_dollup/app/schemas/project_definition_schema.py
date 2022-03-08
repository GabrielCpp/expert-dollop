from uuid import UUID
from json import dumps
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import (
    UserRessourcePaginator,
    UserRessourceQuery,
)
from expert_dollup.shared.starlette_injection import (
    AuthService,
    GraphqlPageHandler,
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.project.project_definition import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_element_controller import (
    find_datasheet_definition_elements,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, datasheet_definition_property_schema_dict, project_definition


@query.field("findProjectDefinition")
@inject_graphql_route(find_project_definition)
@convert_kwargs_to_snake_case
async def resolve_find_project_definition(
    _: Any, info: GraphQLResolveInfo, id: str, find_project_definition: callable
):
    return await find_project_definition(info, UUID(id))


@query.field("findProjectDefintions")
@inject_graphql_handler(GraphqlPageHandler[UserRessourcePaginator[ProjectDefinition]])
@convert_kwargs_to_snake_case
async def resolve_find_project_defintions(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    handler: GraphqlPageHandler[UserRessourcePaginator[ProjectDefinition]],
    after: Optional[str] = None,
):
    user = await info.context.container.get(AuthService).can_perform_required(
        info.context.request,
        ["project_definition:read"],
    )

    result = await handler.handle(
        ProjectDefinitionDto, UserRessourceQuery(user.id), first, after
    )
    return result


@inject_graphql_route(find_datasheet_definition_elements)
@project_definition.field("elementsDefinition")
@convert_kwargs_to_snake_case
async def resolve_elements_definition(
    parent: ProjectDefinitionDto,
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


@project_definition.field("properties")
def resolve_element_definition(
    parent: ProjectDefinitionDto,
    _: GraphQLResolveInfo,
):
    return [
        {"name": name, "schema": schema.dict()}
        for name, schema in parent.properties.items()
    ]
