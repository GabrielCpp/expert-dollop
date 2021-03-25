from ariadne import ObjectType, QueryType

query = QueryType()
datasheet_definition = ObjectType("DatasheetDefinition")
datasheet_definition_element = ObjectType("DatasheetDefinitionElement")
project_definition = ObjectType("ProjectDefinition")
datasheet = ObjectType("Datasheet")
datasheet_element = ObjectType("DatasheetElement")

types = [
    query,
    datasheet_definition,
    datasheet_definition_element,
    project_definition,
    datasheet,
    datasheet_element,
]
