from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.app.controllers.user.user_details import *
from expert_dollup.app.controllers.organization.organization_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, mutation


@query.field("currentUser")
@inject_graphql_route(get_current_user)
@convert_kwargs_to_snake_case
async def resolve_find_project_report(
    _: Any,
    info: GraphQLResolveInfo,
    get_current_user: callable,
):
    try:
        result = await get_current_user(info)
    except RecordNotFound:
        result = None

    return result


@mutation.field("createSingleUserOrganization")
@inject_graphql_route(create_single_user_organization)
@convert_kwargs_to_snake_case
async def resolve_find_project_report(
    _: Any,
    info: GraphQLResolveInfo,
    single_user_organization: dict,
    create_single_user_organization: callable,
):
    result = await create_single_user_organization(
        info, NewSingleUserOrganizationDto.parse_obj(single_user_organization)
    )
    return result
