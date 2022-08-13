from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case, UnionType
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.database_services import UserRessourceQuery, Paginator
from expert_dollup.shared.starlette_injection import (
    GraphqlPageHandler,
    inject_graphql_route,
    inject_graphql_handler,
    AuthService,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.controllers.organization.organization_controller import *
from expert_dollup.app.controllers.project.distributable import *
from .types import query, supplied_item


@query.field("findDistributables")
@inject_graphql_route(get_project_distributables, ["project_id"])
@convert_kwargs_to_snake_case
async def resolve_find_distributable(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
    project_id: str,
    get_project_distributables: callable,
):
    return await get_project_distributables(info, UUID(project_id))


@query.field("findDistributableItems")
@inject_graphql_route(
    get_project_distributable_items, ["project_id", "report_definition_id"]
)
@convert_kwargs_to_snake_case
async def resolve_default_properties(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
    project_id: str,
    report_definition_id: str,
    get_project_distributable_items: callable,
):
    return await get_project_distributable_items(
        info, UUID(project_id), UUID(report_definition_id)
    )


@supplied_item.field("organization")
@inject_graphql_route(get_organization_by_id, ["project_id", "report_definition_id"])
async def supplied_item_organization(
    parent: SuppliedItemDto, info: GraphQLResolveInfo, get_organization_by_id: callable
):
    return await get_organization_by_id(info, parent.organization_id)
