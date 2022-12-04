from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.controllers.definition.aggregate_collection_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.app.controllers.translations_controller import *
from .types import query, mutation, aggregate_collection


@query.field("findAggregateCollection")
@inject_graphql_route(
    find_aggregate_collection_by_id, ["project_definition_id", "collection_id"]
)
@convert_kwargs_to_snake_case
async def resolve_find_definition_aggregate_collections(
    parent: DatasheetElement,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    find_aggregate_collection_by_id,
):
    return await find_aggregate_collection_by_id(
        info, UUID(project_definition_id), UUID(collection_id)
    )


@query.field("findDefinitionAggregateCollections")
@inject_graphql_route(get_aggregate_collections, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_find_definition_aggregate_collections(
    parent: DatasheetElement,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    get_aggregate_collections,
):
    return await get_aggregate_collections(info, UUID(project_definition_id))


@mutation.field("addAggregateCollection")
@inject_graphql_route(add_aggregate_collection, ["project_definition_id"])
@convert_kwargs_to_snake_case
async def resolve_add_aggregate_collection(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection: dict,
    add_aggregate_collection,
):
    for index, schema in enumerate(collection["attributes_schema"]):
        collection["attributes_schema"][index] = collapse_union(
            schema,
            ["details"],
            {
                "INT_FIELD_CONFIG": "int",
                "DECIMAL_FIELD_CONFIG": "decimal",
                "STRING_FIELD_CONFIG": "string",
                "BOOL_FIELD_CONFIG": "bool",
                "STATIC_CHOICE_FIELD_CONFIG": "static_choice",
            },
        )

    return await add_aggregate_collection(
        info,
        UUID(project_definition_id),
        NewAggregateCollectionDto.parse_obj(collection),
    )


@mutation.field("updateAggregateCollection")
@inject_graphql_route(
    update_aggregate_collection, ["project_definition_id", "collection_id"]
)
@convert_kwargs_to_snake_case
async def resolve_update_aggregate_collection(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    collection: dict,
    update_aggregate_collection,
):
    for index, schema in enumerate(collection["attributes_schema"]):
        collection["attributes_schema"][index] = collapse_union(
            schema,
            ["details"],
            {
                "INT_FIELD_CONFIG": "int",
                "DECIMAL_FIELD_CONFIG": "decimal",
                "STRING_FIELD_CONFIG": "string",
                "BOOL_FIELD_CONFIG": "bool",
                "STATIC_CHOICE_FIELD_CONFIG": "static_choice",
            },
        )

    return await update_aggregate_collection(
        info,
        UUID(project_definition_id),
        UUID(collection_id),
        NewAggregateCollectionDto.parse_obj(collection),
    )


@mutation.field("deleteAggregateCollection")
@inject_graphql_route(
    delete_aggregate_collection_by_id, ["project_definition_id", "collection_id"]
)
@convert_kwargs_to_snake_case
async def resolve_delete_aggregate_collection(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    delete_aggregate_collection_by_id,
):
    return await delete_aggregate_collection_by_id(
        info, UUID(project_definition_id), UUID(collection_id)
    )


@aggregate_collection.field("translated")
@inject_graphql_route(find_translation_in_scope, ["ressource_id", "scope"])
@convert_kwargs_to_snake_case
async def resolve_aggregate_collection_translated(
    parent: AggregateCollectionDto,
    info: GraphQLResolveInfo,
    find_translation_in_scope: callable,
):
    translations = await find_translation_in_scope(
        info, parent.project_definition_id, parent.id
    )

    return translations
