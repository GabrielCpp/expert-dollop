from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.project.project_definition import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *

query = QueryType()


@query.field("findProjectDefinition")
@inject_graphql_route(find_project_definition)
@convert_kwargs_to_snake_case
async def resolve_find_datasheet(
    _: Any, info: GraphQLResolveInfo, id: UUID, find_project_definition: callable
):
    return await find_project_definition(info, id)


project_definition = ObjectType("ProjectDefinition")


types = [query, project_definition]