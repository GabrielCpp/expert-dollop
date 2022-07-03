from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.user.user_details import *
from expert_dollup.app.controllers.organisation.organisation_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, mutation
from expert_dollup.shared.database_services.exceptions import RecordNotFound


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


@mutation.field("createSingleUserOrganisation")
@inject_graphql_route(create_single_user_organisation)
@convert_kwargs_to_snake_case
async def resolve_find_project_report(
    _: Any,
    info: GraphQLResolveInfo,
    single_user_organisation: dict,
    create_single_user_organisation: callable,
):
    result = await create_single_user_organisation(
        info, NewSingleUserOrganisationDto.parse_obj(single_user_organisation)
    )
    return result