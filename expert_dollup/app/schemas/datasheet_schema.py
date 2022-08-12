from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from pydantic.tools import parse_obj_as
from expert_dollup.shared.database_services import (
    Paginator,
    UserRessourcePaginator,
    UserRessourceQuery,
)
from expert_dollup.shared.starlette_injection import (
    GraphqlPageHandler,
    inject_graphql_route,
    inject_graphql_handler,
    AuthService,
)
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, datasheet, mutation


@query.field("findDatasheet")
@inject_graphql_route(find_datasheet_by_id)
@convert_kwargs_to_snake_case
async def resolve_find_datasheet(
    _: Any, info: GraphQLResolveInfo, id: str, find_datasheet_by_id: callable
):
    return await find_datasheet_by_id(info, UUID(id))


@datasheet.field("elements")
@inject_graphql_handler(GraphqlPageHandler[Paginator[DatasheetElement]])
@convert_kwargs_to_snake_case
async def resolve_elements(
    parent: DatasheetDto,
    info: GraphQLResolveInfo,
    first: int,
    handler: GraphqlPageHandler[Paginator[DatasheetElement]],
    after: Optional[str] = None,
):
    user = await info.context.container.get(AuthService).can_perform_required(
        info.context.request,
        ["datasheet:read"],
    )

    return await handler.handle(
        DatasheetElementDto,
        DatasheetElementFilter(datasheet_id=parent.id),
        first,
        after,
    )


@mutation.field("createDatasheet")
@inject_graphql_route(add_datasheet)
@convert_kwargs_to_snake_case
async def resolve_create_datasheet(
    parent: DatasheetDto,
    info: GraphQLResolveInfo,
    datasheet: dict,
    add_datasheet: callable,
):
    return await add_datasheet(info, datasheet=parse_obj_as(NewDatasheetDto, datasheet))


@query.field("findDatasheets")
@inject_graphql_handler(GraphqlPageHandler[UserRessourcePaginator[Datasheet]])
@convert_kwargs_to_snake_case
async def resolve_find_datasheets(
    parent: DatasheetDto,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    handler: GraphqlPageHandler[UserRessourcePaginator[Datasheet]],
    after: Optional[str] = None,
):
    user = await info.context.container.get(AuthService).can_perform_required(
        info.context.request,
        ["datasheet:read"],
    )

    return await handler.handle(
        DatasheetDto, UserRessourceQuery(user.organization_id), first, after
    )
