from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.project.project_node import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query


@query.field("findProjectRootSections")
@inject_graphql_route(find_root_sections)
@convert_kwargs_to_snake_case
async def resolve_find_root_sections(
    _: Any, info: GraphQLResolveInfo, project_id: UUID, find_root_sections: callable
):
    return await find_root_sections(info, project_id)


@query.field("findProjectRootSectionContainers")
@inject_graphql_route(find_root_section_nodes)
@convert_kwargs_to_snake_case
async def resolve_find_root_section_nodes(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: UUID,
    root_section_id: UUID,
    find_root_section_nodes: callable,
):
    return await find_root_section_nodes(info, project_id, root_section_id)


@query.field("findProjectFormContent")
@inject_graphql_route(find_form_content)
@convert_kwargs_to_snake_case
async def resolve_find_root_section_nodes(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: UUID,
    form_id: UUID,
    find_form_content: callable,
):
    return await find_form_content(info, project_id, form_id)