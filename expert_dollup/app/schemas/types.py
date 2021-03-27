from ariadne import ObjectType, QueryType, UnionType

query = QueryType()
datasheet_definition = ObjectType("DatasheetDefinition")
datasheet_definition_element = ObjectType("DatasheetDefinitionElement")
project_definition = ObjectType("ProjectDefinition")
project_definition_node = ObjectType("ProjectDefinitionNode")
field_value = UnionType("FieldValue")
node_config_value_type = UnionType("NodeConfigValueType")
datasheet = ObjectType("Datasheet")
datasheet_element = ObjectType("DatasheetElement")

types = [
    query,
    datasheet_definition,
    datasheet_definition_element,
    project_definition,
    datasheet,
    datasheet_element,
    project_definition_node,
    field_value,
    node_config_value_type,
]
