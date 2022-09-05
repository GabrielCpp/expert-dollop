from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from pydantic.tools import parse_obj_as
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_element_controller import *
from expert_dollup.app.dtos import *
from .types import query, datasheet, mutation


@query.field("findDatasheet")
@inject_graphql_route(find_datasheet_by_id)
@convert_kwargs_to_snake_case
async def resolve_find_datasheet(
    _: Any, info: GraphQLResolveInfo, id: str, find_datasheet_by_id: callable
):
    return await find_datasheet_by_id(info, UUID(id))


@datasheet.field("elements")
@inject_graphql_route(find_paginated_datasheet_elements, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_elements(
    parent: DatasheetDto,
    info: GraphQLResolveInfo,
    first: int,
    find_paginated_datasheet_elements,
    after: Optional[str] = None,
):
    user = await info.context.injector.get(AuthService).can_perform_required(
        info.context.request,
        ["datasheet:get"],
    )

    return await find_paginated_datasheet_elements(
        info,
        parent.project_definition_id,
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
@inject_graphql_route(find_paginated_datasheets)
@convert_kwargs_to_snake_case
async def resolve_find_datasheets(
    parent: DatasheetDto,
    info: GraphQLResolveInfo,
    query: str,
    first: int,
    find_paginated_datasheets,
    after: Optional[str] = None,
):
    return await find_paginated_datasheets(info, query, first, after)
