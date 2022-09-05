from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.project.project_details_controller import *
from expert_dollup.app.dtos import *
from .types import query, mutation


@query.field("findProjects")
@inject_graphql_route(find_paginated_project_details)
@convert_kwargs_to_snake_case
async def resolve_find_projects(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    find_paginated_project_details,
    after: Optional[str] = None,
):

    return await find_paginated_project_details(info, query, first, after)


@mutation.field("createProject")
@inject_graphql_route(create_project)
@convert_kwargs_to_snake_case
async def resolve_create_project(
    _: Any,
    info: GraphQLResolveInfo,
    project_details: dict,
    create_project: callable,
):
    result = await create_project(
        info, ProjectDetailsInputDto.parse_obj(project_details)
    )
    return result


@query.field("findProjectDetails")
@inject_graphql_route(find_project_details, ["project_id"])
@convert_kwargs_to_snake_case
async def resolve_create_project(
    _: Any,
    info: GraphQLResolveInfo,
    id: str,
    find_project_details: callable,
):
    result = await find_project_details(info, UUID(id))
    return result
