from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.definition.aggregate_controller import *
from expert_dollup.app.dtos import *
from .types import query, mutation


@query.field("findAggregates")
@inject_graphql_route(
    find_paginated_aggregates, ["project_definition_id", "collection_id"]
)
@convert_kwargs_to_snake_case
async def resolve_add_aggregate(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    query: str,
    first: int,
    find_paginated_aggregates,
    after: Optional[str] = None,
):
    return await find_paginated_aggregates(
        info, UUID(project_definition_id), UUID(collection_id), query, first, after
    )


@mutation.field("addAggregate")
@inject_graphql_route(add_aggregate, ["project_definition_id", "collection_id"])
@convert_kwargs_to_snake_case
async def resolve_add_aggregate(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    aggregate: dict,
    add_aggregate,
):
    for index, schema in enumerate(aggregate["attributes"]):
        aggregate["attributes"][index] = collapse_union(
            schema,
            ["value"],
            {
                "INT_FIELD_VALUE": "int",
                "DECIMAL_FIELD_VALUE": "decimal",
                "STRING_FIELD_VALUE": "string",
                "BOOL_FIELD_VALUE": "bool",
                "REFERENCE_FIELD_VALUE": "reference",
            },
        )

    return await add_aggregate(
        info,
        UUID(project_definition_id),
        UUID(collection_id),
        NewAggregateDto.parse_obj(aggregate),
    )


@mutation.field("updateAggregate")
@inject_graphql_route(
    update_aggregate, ["project_definition_id", "collection_id", "aggregate_id"]
)
@convert_kwargs_to_snake_case
async def resolve_update_aggregate(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    aggregate_id: str,
    replacement: dict,
    update_aggregate,
):
    for index, schema in enumerate(replacement["attributes"]):
        replacement["attributes"][index] = collapse_union(
            schema,
            ["value"],
            {
                "INT_FIELD_VALUE": "int",
                "DECIMAL_FIELD_VALUE": "decimal",
                "STRING_FIELD_VALUE": "string",
                "BOOL_FIELD_VALUE": "bool",
                "REFERENCE_FIELD_VALUE": "reference",
            },
        )

    return await update_aggregate(
        info,
        UUID(project_definition_id),
        UUID(collection_id),
        UUID(aggregate_id),
        NewAggregateDto.parse_obj(replacement),
    )


@mutation.field("deleteAggregate")
@inject_graphql_route(
    delete_collection_aggregate,
    ["project_definition_id", "collection_id", "aggregate_id"],
)
@convert_kwargs_to_snake_case
async def resolve_delete_aggregate(
    _: Any,
    info: GraphQLResolveInfo,
    project_definition_id: str,
    collection_id: str,
    aggregate_id: str,
    delete_collection_aggregate,
):
    return await delete_collection_aggregate(
        info, UUID(project_definition_id), UUID(collection_id), UUID(aggregate_id)
    )
