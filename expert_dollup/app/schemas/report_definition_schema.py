from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.app.controllers.report.report_definition import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import query, mutation


@query.field("findReportDefinitions")
@inject_graphql_route(get_project_def_reports_definitions)
@convert_kwargs_to_snake_case
async def resolve_find_project_definition_reports(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    get_project_def_reports_definitions: callable,
):
    result = await get_project_def_reports_definitions(
        info, UUID(project_definition_id)
    )
    return result


@query.field("findReportDefinition")
@inject_graphql_route(get_report_definition)
@convert_kwargs_to_snake_case
async def resolve_find_report_definition(
    _: Any,
    info: GraphQLResolveInfo,
    report_definition_id: str,
    get_report_definition: callable,
):
    result = await get_report_definition(info, UUID(report_definition_id))
    return result
