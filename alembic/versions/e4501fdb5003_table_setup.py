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
        Column("locale", String(5), nullable=False, primary_key=True),
        Column("name", String, nullable=False, primary_key=True),
        Column("value", String, nullable=False),
    )


def create_project_definition_tables():
    op.create_table(
        "project_definition",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("default_datasheet_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
        Column("plugins", ARRAY(postgresql.UUID(), dimensions=1), nullable=False),
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
        Column("custom_attributes", postgresql.JSON(), nullable=False),
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
        "project_definition_package",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_def_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
        Column("package", String, nullable=False),
    )

    op.create_table(
        "project_definition_struct",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("package_id", String, nullable=False),
        Column("properties", postgresql.JSON(), nullable=True),
        Column("dependencies", postgresql.JSON(), nullable=True),
    )

    op.create_table(
        "project_definition_function",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("code", Text, nullable=False),
        Column("ast", postgresql.JSON(), nullable=True),
        Column("signature", postgresql.JSON(), nullable=True),
        Column("dependencies", postgresql.JSON(), nullable=True),
        Column("struct_id", postgresql.UUID(), nullable=True),
        Column("package_id", postgresql.UUID(), nullable=True),
    )

    op.create_table(
        "project_definition_plugin",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("validation_schema", postgresql.JSON(), nullable=False),
        Column("default_config", postgresql.JSON(), nullable=False),
        Column("form_config", postgresql.JSON(), nullable=False),
        Column("name", String, nullable=False),
    )


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
        Column("custom_attributes", postgresql.JSON(), nullable=False),
    )


def create_datasheet_tables():
    op.create_table(
        "datasheet",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "datasheet_content",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )


def create_plugin_tables():
    op.create_table(
        "project_definition_value_type",
        Column("id", String(16), nullable=False, primary_key=True),
        Column("value_json_schema", postgresql.JSON(), nullable=False),
        Column("attributes_json_schema", postgresql.JSON(), nullable=True),
        Column("template_location", String, nullable=True),
        Column("display_name", String, nullable=False),
    )


def upgrade():
    create_global_table()
    create_project_definition_tables()
    create_project_tables()
    create_plugin_tables()


def downgrade():
    pass
