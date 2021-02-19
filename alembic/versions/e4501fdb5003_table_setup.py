"""Intial database

Revision ID: 2c47a3dd1b88
Revises: 
Create Date: 2020-11-25 22:14:43.244618

"""
import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Boolean, DateTime, Column, Binary, Text, Integer
from alembic import op


# revision identifiers, used by Alembic.
revision = "2c47a3dd1b88"
down_revision = None
branch_labels = None
depends_on = None


def create_global_table():
    op.create_table(
        "settings",
        Column("key", String, nullable=False, primary_key=True),
        Column("value", postgresql.JSON(), nullable=False),
    )

    op.create_table(
        "ressource",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("owner_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
    )

    op.create_index(op.f("ix_ressource_name"), "ressource", ["name"], unique=True)

    op.create_table(
        "translation",
        Column("ressource_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("scope", postgresql.UUID(), nullable=False, primary_key=True),
        Column("locale", String(5), nullable=False, primary_key=True),
        Column("name", String, nullable=False, primary_key=True),
        Column("value", String, nullable=False),
    )

    op.create_index(
        op.f("ix_translation_ressource_id_scope"),
        "translation",
        ["ressource_id", "scope"],
    )


def create_default_value_types(project_definition_value_type):
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
        "value_json_schema": {"type": "null"},
        "attributes_json_schema": {"type": "object"},
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

    op.bulk_insert(
        project_definition_value_type,
        [
            INT_SCHEMA,
            DECIMAL_SCHEMA,
            BOOLEAN_SCHEMA,
            STRING_SCHEMA,
            STATIC_CHOICE_SCHEMA,
            CONTAINER_SCHEMA,
            SECTION_CONTAINER_SCHEMA,
        ],
    )


def create_project_definition_tables():
    op.create_table(
        "project_definition",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("default_datasheet_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_index(op.f("ix_project_definition_name"), "project_definition", ["name"])

    op.create_table(
        "project_definition_container",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_def_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
        Column("is_collection", Boolean, nullable=False),
        Column("instanciate_by_default", Boolean, nullable=False),
        Column("order_index", Integer, nullable=False),
        Column("config", postgresql.JSON(), nullable=False),
        Column("value_type", String, nullable=False),
        Column("default_value", postgresql.JSON(), nullable=True),
        Column("path", String, nullable=False),
        Column("mixed_paths", ARRAY(String, dimensions=1), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_index(
        op.f("ix_project_definition_container_value_type"),
        "project_definition_container",
        ["path"],
    )

    op.create_index(
        op.f("ix_project_definition_container_mixed_paths"),
        "project_definition_container",
        ["mixed_paths"],
        postgresql_using="gin",
    )

    op.create_index(
        op.f("ix_project_definition_container_def_id_name"),
        "project_definition_container",
        ["project_def_id", "name"],
        unique=True,
    )

    op.create_table(
        "project_definition_formula",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_def_id", postgresql.UUID(), nullable=False),
        Column("attached_to_type_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
        Column("expression", String, nullable=False),
        Column("generated_ast", String, nullable=False),
    )

    op.create_index(
        op.f("ix_project_definition_formula_def_id_name"),
        "project_definition_formula",
        ["project_def_id", "name"],
        unique=True,
    )

    op.create_table(
        "project_definition_formula_dependencies",
        Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "depend_on_formula_id", postgresql.UUID(), nullable=False, primary_key=True
        ),
        Column("project_def_id", postgresql.UUID(), nullable=False),
    )

    op.create_table(
        "project_definition_formula_container_dependencies",
        Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "depend_on_container_id",
            postgresql.UUID(),
            nullable=False,
            primary_key=True,
        ),
        Column("project_def_id", postgresql.UUID(), nullable=False),
    )

    project_definition_value_type = op.create_table(
        "project_definition_value_type",
        Column("id", String(32), nullable=False, primary_key=True),
        Column("value_json_schema", postgresql.JSON(), nullable=False),
        Column("attributes_json_schema", postgresql.JSON(), nullable=True),
        Column("template_location", String, nullable=True),
        Column("display_name", String, nullable=False),
    )

    create_default_value_types(project_definition_value_type)


def create_project_tables():
    op.create_table(
        "project",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("is_staged", Boolean, nullable=False),
        Column("project_def_id", postgresql.UUID(), nullable=True),
        Column("datasheet_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "project_container",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_id", postgresql.UUID(), nullable=False),
        Column("type_id", postgresql.UUID(), nullable=False),
        Column("path", String, nullable=False),
        Column("value", postgresql.JSON(), nullable=True),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
        Column("mixed_paths", ARRAY(String, dimensions=1), nullable=False),
    )

    op.execute(
        "ALTER TABLE project_container ADD COLUMN level int GENERATED ALWAYS AS ((CASE WHEN LENGTH(path) > 0 THEN 1 ELSE 0 END) + (LENGTH(path) - LENGTH(REPLACE(path,'/','')))) STORED;"
    )

    op.create_index(
        op.f("ix_project_container_mixed_paths"),
        "project_container",
        ["mixed_paths"],
        postgresql_using="gin",
    )

    op.create_table(
        "project_container_metadata",
        Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("type_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("state", postgresql.JSON(), nullable=False),
    )

    op.create_table(
        "project_formula_cache",
        Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("calculation_details", String, nullable=False),
        Column("result", postgresql.JSON(), nullable=False),
    )


def create_datasheet_tables():
    op.create_table(
        "abstract_element_label_collection",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_def_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
    )

    op.create_table(
        "abstract_element_label",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "abstract_element_label_collection_id", postgresql.UUID(), nullable=False
        ),
        Column("order_index", Integer, nullable=False),
    )

    op.create_table(
        "unit",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    )

    op.create_table(
        "abstract_element",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("unit_id", postgresql.UUID(), nullable=False),
        Column("is_collection", Boolean, nullable=False),
        Column("abstract_element_label_id", postgresql.UUID(), nullable=False),
        Column("properties", postgresql.JSON(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_index(
        op.f("ix_abstract_element_unit_id"),
        "abstract_element",
        ["unit_id"],
    )

    op.create_index(
        op.f("ix_abstract_element_abstract_element_label_id"),
        "abstract_element",
        ["abstract_element_label_id"],
    )

    op.create_table(
        "datasheet",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "datasheet_content",
        Column("datasheet_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "abstract_element_id", postgresql.UUID(), nullable=False, primary_key=True
        ),
        Column(
            "child_element_reference",
            postgresql.UUID(),
            nullable=False,
            primary_key=True,
        ),
        Column("content", postgresql.JSON(), nullable=False),
        Column("original_datasheet_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_index(
        op.f("ix_datasheet_content_abstract_element_id"),
        "datasheet_content",
        ["abstract_element_id"],
    )

    op.create_index(
        op.f("ix_datasheet_content_original_datasheet_id"),
        "datasheet_content",
        ["original_datasheet_id"],
    )


def upgrade():
    create_global_table()
    create_project_definition_tables()
    create_project_tables()
    create_datasheet_tables()


def downgrade():
    pass
