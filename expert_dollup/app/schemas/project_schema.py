from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.project.project import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query, mutation


@query.field("findProjects")
@inject_graphql_handler(GraphqlPageHandler[ProjectDetails])
@convert_kwargs_to_snake_case
async def resolve_find_projects(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    handler: GraphqlPageHandler[ProjectDetails],
    after: Optional[str] = None,
):
    result = await handler.find_all(ProjectDetailsDto, first, after)
    return result


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
@inject_graphql_route(find_project_details)
@convert_kwargs_to_snake_case
async def resolve_create_project(
    _: Any,
    info: GraphQLResolveInfo,
    id: str,
    find_project_details: callable,
):
    result = await find_project_details(info, id)
    return result
