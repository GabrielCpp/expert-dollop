from ariadne import make_executable_schema, load_schema_from_path
from .graphql_context import GraphqlContext
from .datsheet_schema import query as datsheet_queries
from .datasheet_element_schema import datasheet as element_queries

types = [datsheet_queries, element_queries]
type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
schema = make_executable_schema(type_defs, *types)