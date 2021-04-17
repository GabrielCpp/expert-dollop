from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query, mutation, project_definition, project_definition_node


@project_definition.field("rootSections")
@inject_graphql_route(find_root_sections)
@convert_kwargs_to_snake_case
async def resolve_project_definition_root_sections(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    find_root_sections: callable,
):
    result = await find_root_sections(info, parent.id)
    return result


@project_definition.field("rootSectionContainers")
@inject_graphql_route(find_root_section_containers)
@convert_kwargs_to_snake_case
async def resolve_project_definition_root_section_containers(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    root_section_id: UUID,
    find_root_section_containers: callable,
):
    result = await find_root_section_containers(info, parent.id, root_section_id)
    return result


@project_definition.field("formContent")
@inject_graphql_route(find_form_content)
@convert_kwargs_to_snake_case
async def resolve_project_definition_form_content(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    form_id: UUID,
    find_form_content: callable,
):
    result = await find_form_content(info, parent.id, form_id)
    return result


@query.field("findProjectDefinitionRootSections")
@inject_graphql_route(find_root_sections)
@convert_kwargs_to_snake_case
async def resolve_root_sections(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    find_root_sections: callable,
):
    result = await find_root_sections(info, project_def_id)
    return result


@query.field("findProjectDefinitionRootSectionContainers")
@inject_graphql_route(find_root_section_containers)
@convert_kwargs_to_snake_case
async def resolve_root_section_containers(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    root_section_id: UUID,
    find_root_section_containers: callable,
):
    result = await find_root_section_containers(info, project_def_id, root_section_id)
    return result


@query.field("findProjectDefinitionFormContent")
@inject_graphql_route(find_form_content)
@convert_kwargs_to_snake_case
async def resolve_form_content(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    form_id: UUID,
    find_form_content: callable,
):
    result = await find_form_content(info, project_def_id, form_id)
    return result


@query.field("findProjectDefinitionNode")
@inject_graphql_route(find_project_definition_node)
@convert_kwargs_to_snake_case
async def resolve_find_project_definition_node(
    _: Any,
    info: GraphQLResolveInfo,
    project_def_id: UUID,
    id: UUID,
    find_project_definition_node: callable,
):
    result = await find_project_definition_node(info, project_def_id, id)
    return result


@mutation.field("addProjectDefinitionNode")
@inject_graphql_route(create_project_definition_node)
async def resolve_add_project_definition_node(
    _: Any,
    info: GraphQLResolveInfo,
    node: dict,
    create_project_definition_node: callable,
):
    node = collapse_union(
        node,
        ["config", "fieldDetails"],
        {
            "INT_FIELD_CONFIG": "int",
            "DECIMAL_FIELD_CONFIG": "decimal",
            "STRING_FIELD_CONFIG": "string",
            "BOOL_FIELD_CONFIG": "bool",
            "STATIC_CHOICE_FIELD_CONFIG": "staticChoice",
            "COLLAPSIBLE_CONTAINER_FIELD_CONFIG": "collapsibleContainer",
        },
    )

    result = await create_project_definition_node(
        info, ProjectDefinitionNodeDto.parse_obj(node)
    )

    return result