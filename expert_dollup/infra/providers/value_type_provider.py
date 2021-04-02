

INT_SCHEMA = {
    "id": "INT",
    "value_json_schema": {"maximum": 100000, "minimum": 0, "type": "integer"},
    "attributes_json_schema": {"type": "object"},
    "template_location": None,
    "display_name": "integer",
}

DECIMAL_SCHEMA = {
    "id": "DECIMAL",
    "value_json_schema": {"maximum": 100000, "minimum": -100000, "type": "number"},
    "attributes_json_schema": {"type": "object"},
    "template_location": None,
    "display_name": "decimal",
}

BOOLEAN_SCHEMA = {
    "id": "BOOLEAN",
    "value_json_schema": {"type": "boolean"},
    "attributes_json_schema": {"type": "object"},
    "template_location": None,
    "display_name": "boolean",
}

STRING_SCHEMA = {
    "id": "STRING",
    "value_json_schema": {"maxLength": 200, "minLength": 1, "type": "string"},
    "attributes_json_schema": {"type": "object"},
    "template_location": None,
    "display_name": "string",
}

STATIC_CHOICE_SCHEMA = {
    "id": "STATIC_CHOICE",
    "value_json_schema": {"type": "string"},
    "attributes_json_schema": {
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
    "template_location": None,
    "display_name": "string",
}

CONTAINER_SCHEMA = {
    "id": "CONTAINER",
        },
    },
    "template_location": None,
    "display_name": "container",
}
SECTION_CONTAINER_SCHEMA = {
    "id": "SECTION_CONTAINER",
    "value_json_schema": {"type": "null"},
    "attributes_json_schema": {
        "type": "object",
        "properties": {
            "is_collection": {"type": "boolean"},
        },
    },
    "template_location": None,
    "display_name": "container",
}


class ValueTypeProvider:
    def get_schema_per_type(self) -> Dict[str, dict]:
        return {
            
        }