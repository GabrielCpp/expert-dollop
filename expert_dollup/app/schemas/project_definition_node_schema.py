from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
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
@inject_graphql_route(find_root_section_nodes)
@convert_kwargs_to_snake_case
async def resolve_project_definition_root_section_nodes(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    root_section_id: str,
    find_root_section_nodes: callable,
):
    result = await find_root_section_nodes(info, parent.id, UUID(root_section_id))
    return result


@project_definition.field("formContent")
@inject_graphql_route(find_form_content)
@convert_kwargs_to_snake_case
async def resolve_project_definition_form_content(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    form_id: str,
    find_form_content: callable,
):
    result = await find_form_content(info, parent.id, UUID(form_id))
    return result


@query.field("findProjectDefinitionRootSections")
@inject_graphql_route(find_root_sections)
@convert_kwargs_to_snake_case
async def resolve_root_sections(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    find_root_sections: callable,
):
    result = await find_root_sections(info, UUID(project_definition_id))
    return result


@query.field("findProjectDefinitionRootSectionContainers")
@inject_graphql_route(find_root_section_nodes)
@convert_kwargs_to_snake_case
async def resolve_root_section_nodes(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    root_section_id: str,
    find_root_section_nodes: callable,
):
    result = await find_root_section_nodes(
        info, UUID(project_definition_id), UUID(root_section_id)
    )
    return result


@query.field("findProjectDefinitionFormContent")
@inject_graphql_route(find_form_content)
@convert_kwargs_to_snake_case
async def resolve_form_content(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    form_id: str,
    find_form_content: callable,
):
    result = await find_form_content(info, UUID(project_definition_id), UUID(form_id))
    return result


@query.field("findProjectDefinitionNode")
@inject_graphql_route(find_project_definition_node)
@convert_kwargs_to_snake_case
async def resolve_find_project_definition_node(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    id: str,
    find_project_definition_node: callable,
):
    result = await find_project_definition_node(
        info, UUID(project_definition_id), UUID(id)
    )
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
            "STATIC_NUMBER_FIELD_CONFIG": "staticNumberFieldConfig",
        },
    )

    result = await create_project_definition_node(
        info, ProjectDefinitionNodeDto.parse_obj(node)
    )

    return result


@project_definition_node.field("translations")
@inject_graphql_route(find_translation_in_scope)
async def resolve_project_definition_node_translations(
    parent: ProjectDefinitionNodeDto,
    info: GraphQLResolveInfo,
    find_translation_in_scope: callable,
):
    return await find_translation_in_scope(
        info, parent.project_definition_id, parent.id
    )
