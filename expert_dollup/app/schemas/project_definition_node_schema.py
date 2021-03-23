from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *

project_definition = ObjectType("ProjectDefinition")


@project_definition.field("rootSections")
@inject_graphql_route(find_root_sections)
@convert_kwargs_to_snake_case
async def resolve_root_sections(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    find_root_sections: callable,
):
    return await find_root_sections(info, project_def_id)


@project_definition.field("rootSectionContainers")
@inject_graphql_route(find_root_section_containers)
@convert_kwargs_to_snake_case
async def resolve_root_section_containers(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    root_section_id: UUID,
    find_root_section_containers: callable,
):
    return await find_root_section_containers(info, project_def_id, root_section_id)


@project_definition.field("formContent")
@inject_graphql_route(find_form_content)
@convert_kwargs_to_snake_case
async def resolve_form_content(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    form_id: UUID,
    find_form_content: callable,
):
    return await find_form_content(info, project_def_id, form_id)


types = [project_definition]