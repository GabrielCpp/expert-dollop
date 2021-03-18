from ariadne import make_executable_schema, load_schema_from_path
from .datsheet_schema import query as datsheet_queries
from .graphql_context import GraphqlContext

types = [datsheet_queries]
type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
schema = make_executable_schema(type_defs, *types)