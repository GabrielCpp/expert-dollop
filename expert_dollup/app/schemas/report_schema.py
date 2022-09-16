from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.report.report import *
from expert_dollup.app.dtos import *
from .types import query, mutation


@query.field("findProjectReport")
@inject_graphql_route(get_project_report)
@convert_kwargs_to_snake_case
async def resolve_find_project_report(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: str,
    report_definition_id: str,
    get_project_report: callable,
):
    result = await get_project_report(
        info, UUID(project_id), UUID(report_definition_id)
    )
    return result
