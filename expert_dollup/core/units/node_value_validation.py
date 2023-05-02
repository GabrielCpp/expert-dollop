from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.shared.validation import ValidationError
from expert_dollup.core.domains import *
from typing import Optional

BOOL_JSON_SCHEMA = {"type": "boolean"}
INT_JSON_SCHEMA = {"type": "integer", "minimum": 0, "maximum": 100000}
DECIMAL_JSON_SCHEMA = {"type": "number", "minimum": -100000, "maximum": 100000}
STRING_JSON_SCHEMA = {
    "type": "string",
    "minLength": 1,
    "maxLength": 200,
}


def make_static_choice_schema(config: StaticChoiceFieldConfig):
    return {
        "type": "string",
        "enum": [o.id for o in config.options],
    }


TYPE_TO_SCHEMA = {
    IntFieldConfig: lambda _: INT_JSON_SCHEMA,
    StaticChoiceFieldConfig: lambda n: make_static_choice_schema(n.field_details),
    DecimalFieldConfig: lambda _: DECIMAL_JSON_SCHEMA,
    StringFieldConfig: lambda _: STRING_JSON_SCHEMA,
    BoolFieldConfig: lambda _: BOOL_JSON_SCHEMA,
}


def make_schema(node_definition: ProjectDefinitionNode) -> Optional[dict]:
    TYPE_TO_SCHEMA.get(type(node_definition.field_details))
    make_it = TYPE_TO_SCHEMA.get(type(node_definition.field_details))

    if make_it is None:
        return None

    return make_it(node_definition)


class NodeValueValidation:
    def __init__(self, schema_validator: SchemaValidator):
        self.schema_validator = schema_validator

    def validate_value(
        self, node_definition: ProjectDefinitionNode, value: PrimitiveWithNoneUnion
    ) -> None:
        schema = make_schema(node_definition)

        if schema is None:
            return

        self.schema_validator.validate_instance_of(schema, value)
