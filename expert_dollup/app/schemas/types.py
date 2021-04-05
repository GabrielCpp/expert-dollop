import json
from ariadne import (
    ObjectType,
    QueryType,
    UnionType,
    ScalarType,
    make_executable_schema,
    load_schema_from_path,
    snake_case_fallback_resolvers,
)
from expert_dollup.shared.starlette_injection import GraphqlContext

query = QueryType()
datasheet_definition = ObjectType("DatasheetDefinition")
datasheet_definition_element = ObjectType("DatasheetDefinitionElement")
project_definition = ObjectType("ProjectDefinition")
project_definition_node = ObjectType("ProjectDefinitionNode")
field_value = UnionType("FieldValue")
field_details_union_type = UnionType("FieldDetailsUnion")
datasheet = ObjectType("Datasheet")
datasheet_element = ObjectType("DatasheetElement")
json_schema_scalar = ScalarType("JsonSchema")

types = [
    query,
    datasheet_definition,
    datasheet_definition_element,
    project_definition,
    datasheet,
    datasheet_element,
    project_definition_node,
    field_value,
    field_details_union_type,
    json_schema_scalar,
]


@json_schema_scalar.serializer
def serialize_json_schema(value):
    return json.dumps(value)


@json_schema_scalar.value_parser
def parse_json_schema_value(value):
    if value:
        return json.loads(value)


@json_schema_scalar.literal_parser
def parse_json_schema_litteral(ast):
    value = str(ast.value)
    return parse_json_schema_value(value)


def build_schema():
    type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
    schema = make_executable_schema(type_defs, *types, snake_case_fallback_resolvers)
    return schema
