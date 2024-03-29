import json
from uuid import UUID
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
from expert_dollup.shared.starlette_injection import GraphqlContext

mutation = MutationType()
query = QueryType()
datasheet_definition_property_schema_dict = ObjectType(
    "DatasheetDefinitionPropertySchemaDict"
)
datasheet_definition_element = ObjectType("DatasheetDefinitionElement")
project_definition = ObjectType("ProjectDefinition")
project_details = ObjectType("ProjectDetails")
project_definition_node = ObjectType("ProjectDefinitionNode")
static_choice_option = ObjectType("StaticChoiceOption")
field_value = UnionType("FieldValue")
field_details_union_type = UnionType("FieldDetailsUnion")
datasheet = ObjectType("Datasheet")
datasheet_element = ObjectType("DatasheetElement")
json_schema_scalar = ScalarType("JsonSchema")
graphql_uuid = ScalarType("UUID")
supplied_item = ObjectType("SuppliedItem")
project_node_meta = ObjectType("ProjectNodeMeta")

types = [
    mutation,
    query,
    datasheet_definition_element,
    project_definition,
    datasheet,
    datasheet_element,
    project_details,
    project_definition_node,
    field_value,
    field_details_union_type,
    json_schema_scalar,
    supplied_item,
    static_choice_option,
]


@json_schema_scalar.serializer
def serialize_json_schema(value):
    return json.dumps(value)


@json_schema_scalar.value_parser
def parse_json_schema_value(value):
    if value:
        return json.loads(value)


@json_schema_scalar.literal_parser
def parse_json_schema_litteral(ast, _):
    value = str(ast.value)
    return parse_json_schema_value(value)


#


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
