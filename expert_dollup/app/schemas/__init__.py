from ariadne import make_executable_schema, load_schema_from_path

types = []
type_defs = load_schema_from_path("./expert_dollup/app/schemas/schema.graphql")
schema = make_executable_schema(type_defs, *types)