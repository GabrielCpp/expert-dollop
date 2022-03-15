from pydantic import parse_obj_as
from expert_dollup.app.dtos import *


def test_deserialize_node_config_dto():
    result = parse_obj_as(
        ProjectDefinitionNodeDto,
        {
            "id": "11ec6fcd-3fcf-aa70-bcc3-42010a800002",
            "project_definition_id": "11ec6fcd-3fc8-c2b2-bcc3-42010a800002",
            "name": "smxhu",
            "is_collection": False,
            "instanciate_by_default": True,
            "order_index": 1,
            "config": {
                "translations": {"label": "smxhu", "help_text_name": "smxhu_help_text"},
                "triggers": [],
                "field_details": {
                    "pass_to_translation": True,
                    "precision": 3,
                    "unit": "foot",
                },
                "value_validator": {"type": "string", "minLength": 1, "maxLength": 200},
                "meta": {"is_visible": True},
            },
            "default_value": {"text": "0"},
            "path": [
                "11ec6fcd-3fce-0186-bcc3-42010a800002",
                "11ec6fcd-3fcf-9e85-bcc3-42010a800002",
                "11ec6fcd-3fcf-a1f4-bcc3-42010a800002",
                "11ec6fcd-3fcf-a4e8-bcc3-42010a800002",
            ],
            "creation_date_utc": "2022-03-14T21:16:03.141507+00:00",
        },
    )

    assert type(result.config.field_details) is StaticNumberFieldConfigDto