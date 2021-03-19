from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from typing import Any, Optional
from uuid import UUID

from expert_dollup.shared.starlette_injection import inject_graphql_handler
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.app.dtos import DatasheetDto, DatasheetElementDto
from expert_dollup.infra.services import DatasheetElementService
from expert_dollup.core.domains import DatasheetElementFilter

datasheet = ObjectType("Datasheet")


@datasheet.field("elements")
@inject_graphql_handler(
    GraphqlPageHandler[DatasheetElementService, DatasheetElementDto]
)
@convert_kwargs_to_snake_case
async def resolve_find_datsheet(
    parent: DatasheetDto,
    info: GraphQLResolveInfo,
    first: int,
    handler: GraphqlPageHandler[DatasheetElementService, DatasheetElementDto],
    after: Optional[str] = None,
):
    return await handler.handle(
        DatasheetElementFilter(datasheet_id=parent.id), first, after
    )
