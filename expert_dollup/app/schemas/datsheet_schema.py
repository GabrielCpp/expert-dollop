from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from typing import Any, Optional
from uuid import UUID

from expert_dollup.shared.starlette_injection import inject_graphql_route
from expert_dollup.app.controllers.datasheet.datasheet_controller import (
    find_datasheet_by_id,
)

query = QueryType()


@query.field("findDatasheet")
@inject_graphql_route(find_datasheet_by_id)
@convert_kwargs_to_snake_case
async def resolve_find_datsheet(
    _: Any, info: GraphQLResolveInfo, id: UUID, find_datasheet_by_id: callable
):
    return await find_datasheet_by_id(info, id)
