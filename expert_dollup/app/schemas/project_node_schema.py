from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.project.project_node import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query, mutation
from pydantic import parse_obj_as


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


@mutation.field("updateProjectField")
@inject_graphql_route(mutate_project_field)
@convert_kwargs_to_snake_case
async def resolve_update_project_field(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: UUID,
    node_id: UUID,
    value: PrimitiveWithNoneUnion,
    mutate_project_field: callable,
):
    value = collapse_union(
        value,
        [],
        {
            "INT_FIELD_VALUE": "int",
            "DECIMAL_FIELD_VALUE": "decimal",
            "STRING_FIELD_VALUE": "string",
            "BOOL_FIELD_VALUE": "bool",
        },
    )

    return await mutate_project_field(info, project_id, node_id, value)


@mutation.field("updateProjectFields")
@inject_graphql_route(mutate_project_fields)
@convert_kwargs_to_snake_case
async def resolve_update_project_fields(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: UUID,
    updates: list,
    mutate_project_fields: callable,
):
    updates = [
        collapse_union(
            update,
            ["value"],
            {
                "INT_FIELD_VALUE": "int",
                "DECIMAL_FIELD_VALUE": "decimal",
                "STRING_FIELD_VALUE": "string",
                "BOOL_FIELD_VALUE": "bool",
            },
        )
        for update in updates
    ]

    return await mutate_project_fields(
        info, project_id, parse_obj_as(List[FieldUpdateInputDto], updates)
    )


@mutation.field("addProjectCollectionItem")
@inject_graphql_route(add_project_collection)
@convert_kwargs_to_snake_case
async def resolve_add_project_collection_item(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: UUID,
    collection_target: dict,
    add_project_collection: callable,
):
    return await add_project_collection(
        info,
        project_id,
        parse_obj_as(ProjectNodeCollectionTargetDto, collection_target),
    )


@mutation.field("cloneProjectCollection")
@inject_graphql_route(clone_project_collection)
@convert_kwargs_to_snake_case
async def resolve_clone_project_collection(
    _: Any,
    info: GraphQLResolveInfo,
    project_id: UUID,
    collection_node_id: UUID,
    clone_project_collection: callable,
):
    return await clone_project_collection(
        info,
        project_id,
        collection_node_id,
    )
