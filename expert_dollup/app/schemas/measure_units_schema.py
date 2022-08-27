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
from expert_dollup.app.controllers.measure_units_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, mutation
from expert_dollup.shared.database_services.exceptions import RecordNotFound


@query.field("units")
@inject_graphql_route(get_measure_units)
@convert_kwargs_to_snake_case
async def units(_: Any, info: GraphQLResolveInfo, get_measure_units: callable):
    return await get_measure_units(info)
