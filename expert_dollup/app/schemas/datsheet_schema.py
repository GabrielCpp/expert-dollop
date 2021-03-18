from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from typing import Any
from uuid import UUID

from expert_dollup.app.controllers.datasheet.datasheet_controller import (
    find_datasheet_by_id,
    DatasheetUseCase,
    RequestHandler,
)

query = QueryType()


@query.field("findDatasheet")
@convert_kwargs_to_snake_case
async def resolve_find_datsheet(_: Any, info: GraphQLResolveInfo, id: UUID):

    return await find_datasheet_by_id(
        id,
        usecase=info.context.container.get(DatasheetUseCase),
        handler=info.context.container.get(RequestHandler),
    )
