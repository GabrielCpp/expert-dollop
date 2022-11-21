import json
from uuid import UUID
from typing import Dict, Type
from ariadne import (
    ObjectType,
    QueryType,
    MutationType,
    UnionType,
    ScalarType,
    make_executable_schema,
    load_schema_from_path,
    snake_case_fallback_resolvers,
)
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlContext
from expert_dollup.app.dtos import *

mutation = MutationType()
query = QueryType()
project_definition = ObjectType("ProjectDefinition")
project_details = ObjectType("ProjectDetails")
project_definition_node = ObjectType("ProjectDefinitionNode")
static_choice_option = ObjectType("StaticChoiceOption")
datasheet = ObjectType("Datasheet")
datasheet_element = ObjectType("DatasheetElement")
graphql_uuid = ScalarType("UUID")
supplied_item = ObjectType("SuppliedItem")
project_node_meta = ObjectType("ProjectNodeMeta")
aggregate_collection = ObjectType("AggregateCollection")


def define_union_type(name: str, mapping: Dict[Type, str]) -> UnionType:
    union_type = UnionType(name)

    @union_type.type_resolver
    def resolve_union_type(target, info: GraphQLResolveInfo, context: GraphqlContext):
        target_type = type(target)

        if not target_type in mapping:
            raise LookupError(f"Field type not found {target_type}")

        return mapping[target_type]

    return union_type


types = [
    mutation,
    query,
    project_definition,
    datasheet,
    datasheet_element,
    project_details,
    project_definition_node,
    define_union_type("PrimitiveWithReferenceUnion", value_type_lookup_map),
    define_union_type("FieldDetailsUnion", config_type_lookup_map),
    define_union_type("AttributeDetailsUnion", attribute_details_union),
    supplied_item,
    static_choice_option,
    aggregate_collection,
]


@graphql_uuid.serializer
def serialize_graphql_uuid(value):
    return str(value)


@graphql_uuid.value_parser
def parse_graphql_uuid_value(value):
    if value:
        return UUID(value)


@graphql_uuid.literal_parser
def parse_graphql_uuid_litteral(ast, _):
    value = str(ast.value)
    return parse_graphql_uuid_value(value)


def build_schema():
    type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
    schema = make_executable_schema(type_defs, *types, snake_case_fallback_resolvers)
    return schema
