from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import (
    query,
    mutation,
    project_definition,
    project_definition_node,
    static_choice_option,
)


@project_definition.field("rootSections")
@inject_graphql_route(find_definition_root_sections, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_project_definition_root_sections(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    find_definition_root_sections: callable,
):
    result = await find_definition_root_sections(info, parent.id)
    return result


@project_definition.field("rootSectionContainers")
@inject_graphql_route(find_definition_root_section_nodes, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_project_definition_root_section_nodes(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    root_section_id: str,
    find_definition_root_section_nodes: callable,
):
    return await find_definition_root_section_nodes(
        info, parent.id, UUID(root_section_id)
    )


@project_definition.field("formContent")
@inject_graphql_route(
    find_definition_form_content, ["project_definition_id", "form_id"]
)
@convert_kwargs_to_snake_case
async def resolve_project_definition_form_content(
    parent: ProjectDefinitionDto,
    info: GraphQLResolveInfo,
    form_id: str,
    find_definition_form_content: callable,
):
    result = await find_definition_form_content(info, parent.id, UUID(form_id))
    return result


@query.field("findProjectDefinitionRootSections")
@inject_graphql_route(find_definition_root_sections, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_root_sections(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    find_definition_root_sections: callable,
):
    result = await find_definition_root_sections(info, UUID(project_definition_id))
    return result


@query.field("findProjectDefinitionRootSectionContainers")
@inject_graphql_route(
    find_definition_root_section_nodes, ["project_definition_id", "root_section_id"]
)
@convert_kwargs_to_snake_case
async def resolve_root_section_nodes(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    root_section_id: str,
    find_definition_root_section_nodes: callable,
):
    result = await find_definition_root_section_nodes(
        info, UUID(project_definition_id), UUID(root_section_id)
    )
    return result


@query.field("findProjectDefinitionFormContent")
@inject_graphql_route(
    find_definition_form_content, ["project_definition_id", "form_id"]
)
@convert_kwargs_to_snake_case
async def resolve_form_content(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    form_id: str,
    find_definition_form_content: callable,
):
    return await find_definition_form_content(
        info, UUID(project_definition_id), UUID(form_id)
    )


@query.field("findProjectDefinitionNode")
@inject_graphql_route(
    find_project_definition_node, ["project_definition_id", "node_id"]
)
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


@mutation.field("deleteProjectDefinitionNode")
@inject_graphql_route(
    delete_project_definition_node, ["project_definition_id", "node_id"]
)
@convert_kwargs_to_snake_case
async def resolve_update_project_definition_node(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    node_id: str,
    delete_project_definition_node,
):
    await delete_project_definition_node(
        info,
        UUID(project_definition_id),
        UUID(node_id),
    )

    return node_id


@mutation.field("addProjectDefinitionNode")
@inject_graphql_route(create_project_definition_node, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_add_project_definition_node(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    node: dict,
    create_project_definition_node: callable,
):
    node = collapse_union(
        node,
        ["field_details"],
        {
            "INT_FIELD_CONFIG": "int",
            "DECIMAL_FIELD_CONFIG": "decimal",
            "STRING_FIELD_CONFIG": "string",
            "BOOL_FIELD_CONFIG": "bool",
            "STATIC_CHOICE_FIELD_CONFIG": "static_choice",
            "COLLAPSIBLE_CONTAINER_FIELD_CONFIG": "collapsible_container",
            "STATIC_NUMBER_FIELD_CONFIG": "static_number_field_config",
        },
    )

    result = await create_project_definition_node(
        info,
        UUID(project_definition_id),
        ProjectDefinitionNodeCreationDto.parse_obj(node),
    )

    return result


@mutation.field("updateProjectDefinitionNode")
@inject_graphql_route(
    update_project_definition_node, ["project_definition_id", "node_id"]
)
@convert_kwargs_to_snake_case
async def resolve_update_project_definition_node(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    node_id: str,
    node: dict,
    update_project_definition_node: callable,
):
    node = collapse_union(
        node,
        ["field_details"],
        {
            "INT_FIELD_CONFIG": "int",
            "DECIMAL_FIELD_CONFIG": "decimal",
            "STRING_FIELD_CONFIG": "string",
            "BOOL_FIELD_CONFIG": "bool",
            "STATIC_CHOICE_FIELD_CONFIG": "static_choice",
            "COLLAPSIBLE_CONTAINER_FIELD_CONFIG": "collapsible_container",
            "STATIC_NUMBER_FIELD_CONFIG": "static_number_field_config",
        },
    )

    result = await update_project_definition_node(
        info,
        UUID(project_definition_id),
        UUID(node_id),
        ProjectDefinitionNodeCreationDto.parse_obj(node),
    )

    return result


@project_definition_node.field("translated")
@inject_graphql_route(find_translation_in_scope, ["ressource_id", "scope"])
@convert_kwargs_to_snake_case
async def resolve_project_definition_node_translated(
    parent: ProjectDefinitionNodeDto,
    info: GraphQLResolveInfo,
    find_translation_in_scope: callable,
):
    translations = await find_translation_in_scope(
        info, parent.project_definition_id, parent.id
    )

    return translations


@query.field("findDefinitionFormulaFieldMix")
@inject_graphql_route(find_definition_formula_field_mix, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_find_project_definition(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    query: str,
    first: int,
    find_definition_formula_field_mix,
    after: Optional[str] = None,
):
    return await find_definition_formula_field_mix(
        info, UUID(project_definition_id), query, first, after
    )
