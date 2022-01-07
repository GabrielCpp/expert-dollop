from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.report.report_definition import (
    get_project_def_reports_definitions,
)
from .types import project_details


@project_details.field("reportDefinitions")
@inject_graphql_route(get_project_def_reports_definitions)
@convert_kwargs_to_snake_case
async def resolve_find_root_section_nodes(
    parent: Any,
    info: GraphQLResolveInfo,
    get_project_def_reports_definitions: callable,
):
    return await get_project_def_reports_definitions(info, parent.project_def_id)
