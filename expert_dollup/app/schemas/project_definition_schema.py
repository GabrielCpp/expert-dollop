from uuid import UUID
from json import dumps
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.app.controllers.definition.definition_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import (
    query,
    project_definition,
    mutation,
)


@query.field("findProjectDefinition")
@inject_graphql_route(find_project_definition)
@convert_kwargs_to_snake_case
async def resolve_find_project_definition(
    _: Any, info: GraphQLResolveInfo, id: str, find_project_definition: callable
):
    return await find_project_definition(info, UUID(id))


@query.field("findProjectDefintions")
@inject_graphql_route(find_paginated_project_definitions)
@convert_kwargs_to_snake_case
async def resolve_find_project_defintions(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    find_paginated_project_definitions,
    after: Optional[str] = None,
):
    return await find_paginated_project_definitions(info, query, first, after)


@mutation.field("addProjectDefinition")
@inject_graphql_route(create_project_definition, [])
@convert_kwargs_to_snake_case
async def resolve_add_project_definition(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    definition_input: dict,
    create_project_definition,
):
    return await create_project_definition(
        info, NewDefinitionDto.parse_obj(definition_input)
    )
