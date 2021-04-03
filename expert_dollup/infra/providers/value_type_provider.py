from expert_dollup.core.domains import ValueTypeSchema, ValueType
from typing import List, Dict


class ValueTypeProvider:
    def __init__(self):
        self.schema_per_type_cache = None

    def get_schemas(self) -> List[ValueTypeSchema]:
        return [
            ValueTypeSchema(
                id="INT",
                validator={"maximum": 100000, "minimum": 0, "type": "integer"},
                display_name="integer",
            ),
            ValueTypeSchema(
                id="DECIMAL",
                validator={"maximum": 100000, "minimum": -100000, "type": "number"},
                display_name="decimal",
            ),
            ValueTypeSchema(
                id="BOOLEAN", validator={"type": "boolean"}, display_name="boolean"
            ),
            ValueTypeSchema(
                id="STRING",
                validator={"maxLength": 200, "minLength": 1, "type": "string"},
                display_name="string",
            ),
            ValueTypeSchema(
                id="STATIC_CHOICE",
                validator={
                    "type": "object",
                    "properties": {
                        "options": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "help_text": {"type": "string"},
                                    "id": {"type": "string"},
                                    "label": {"type": "string"},
                                },
                            },
                        },
                        "validator": {"type": "object"},
                    },
                },
                display_name="static_choice",
            ),
            ValueTypeSchema(id="CONTAINER", validator=None, display_name="container"),
            ValueTypeSchema(
                id="SECTION_CONTAINER",
                validator={
                    "type": "object",
                    "properties": {
                        "is_collection": {"type": "boolean"},
                    },
                },
                display_name="section_container",
            ),
        ]

    def get_schema_per_type(self) -> Dict[ValueType, ValueTypeSchema]:
        if self.schema_per_type_cache is None:
            self.schema_per_type_cache = {
                value_type.id: value_type for value_type in self.get_schemas()
            }

        return self.schema_per_type_cache
