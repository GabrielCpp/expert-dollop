from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import (
    UserRessourcePaginator,
    UserRessourceQuery,
)
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
    GraphqlPageHandler,
    AuthService,
)
from expert_dollup.app.controllers.project.project import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, mutation


@query.field("findProjects")
@inject_graphql_handler(GraphqlPageHandler[UserRessourcePaginator[ProjectDetails]])
@convert_kwargs_to_snake_case
async def resolve_find_projects(
    _: Any,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    handler: GraphqlPageHandler[UserRessourcePaginator[ProjectDetails]],
    after: Optional[str] = None,
):
    user = await info.context.container.get(AuthService).can_perform_required(
        info.context.request,
        ["project:read"],
    )

    result = await handler.handle(
        ProjectDetailsDto, UserRessourceQuery(user.organization_id), first, after
    )

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
