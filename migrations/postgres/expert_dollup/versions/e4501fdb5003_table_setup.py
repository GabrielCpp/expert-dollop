"""Initial database

Revision ID: 2c47a3dd1b88
Revises: 
Create Date: 2020-11-25 22:14:43.244618

"""
import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Boolean, DateTime, Column, Text, Integer
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
        "translation",
        Column("id", postgresql.UUID(), nullable=False),
        Column("ressource_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("locale", String(5), nullable=False, primary_key=True),
        Column("name", String, nullable=False, primary_key=True),
        Column("scope", postgresql.UUID(), nullable=False),
        Column("value", String, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_index(
        op.f("ix_translation_id"),
        "translation",
        ["id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_translation_ressource_id_scope"),
        "translation",
        ["ressource_id", "scope"],
    )


def create_project_definition_tables():
    op.create_table(
        "project_definition",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("default_datasheet_id", postgresql.UUID(), nullable=False),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "project_definition_node",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
        Column("path", String, nullable=False),
        Column("level", Integer, nullable=False),
        Column("display_query_internal_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
        Column("config", postgresql.JSON(), nullable=False),
        Column("_version", Integer, nullable=False),
    )

    op.create_index(
        op.f("ix_project_definition_node_project_definition_id_path"),
        "project_definition_node",
        ["project_definition_id", "path"],
    )

    op.create_index(
        op.f("ix_project_definition_node_display_query_internal_id"),
        "project_definition_node",
        ["display_query_internal_id"],
    )

    op.create_index(
        op.f("ix_project_definition_node_def_id_name"),
        "project_definition_node",
        ["project_definition_id", "name"],
        unique=True,
    )


def create_project_tables():
    op.create_table(
        "project",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("is_staged", Boolean, nullable=False),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("datasheet_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "project_node",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_id", postgresql.UUID(), nullable=False),
        Column("type_id", postgresql.UUID(), nullable=False),
        Column("type_name", String, nullable=False),
        Column("path", String, nullable=False),
        Column("value", postgresql.JSON(), nullable=True),
        Column("label", String, nullable=True),
        Column("level", Integer, nullable=False),
        Column("type_path", String, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
        Column("display_query_internal_id", postgresql.UUID(), nullable=False),
    )

    op.create_index(
        op.f("ix_project_node_display_query_internal_id"),
        "project_node",
        ["display_query_internal_id"],
    )

    op.create_index(
        op.f("ix_project_node_project_id_path"),
        "project_node",
        ["project_id", "path"],
    )

    op.create_index(
        op.f("ix_project_node_project_id_level"),
        "project_node",
        ["project_id", "level"],
    )

    op.create_table(
        "project_node_metadata",
        Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("type_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("state", postgresql.JSON(), nullable=False),
        Column("definition", postgresql.JSON(), nullable=False),
        Column("display_query_internal_id", postgresql.UUID(), nullable=False),
    )

    op.create_index(
        op.f("ix_project_node_metadata_display_query_internal_id"),
        "project_node_metadata",
        ["display_query_internal_id"],
    )


def create_datasheet_tables():
    op.create_table(
        "unit",
        Column("id", String(16), nullable=False, primary_key=True),
    )

    op.create_table(
        "project_definition",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("properties", postgresql.JSON(), nullable=False),
    )

    op.create_table(
        "datasheet_definition_label_collection",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
        Column("attributes_schema", postgresql.JSON(), nullable=False),
    )

    op.create_table(
        "datasheet_definition_label",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "label_collection_id",
            postgresql.UUID(),
            nullable=False,
        ),
        Column("order_index", Integer, nullable=False),
        Column("name", String, nullable=False),
        Column("attributes", postgresql.JSON(), nullable=False),
    )

    op.create_index(
        op.f("ix_datasheet_definition_label_label_collection_id"),
        "datasheet_definition_label",
        ["label_collection_id"],
    )

    op.create_table(
        "datasheet_definition_element",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("unit_id", String, nullable=False),
        Column("is_collection", Boolean, nullable=False),
        Column("name", String(64), nullable=False),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("order_index", Integer, nullable=False),
        Column("default_properties", postgresql.JSON(), nullable=False),
        Column("tags", ARRAY(postgresql.UUID(), dimensions=1), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "datasheet",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("name", String, nullable=False),
        Column("is_staged", Boolean, nullable=False),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("from_datasheet_id", postgresql.UUID(), nullable=True),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "datasheet_element",
        Column("datasheet_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("element_def_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "child_element_reference",
            postgresql.UUID(),
            nullable=False,
            primary_key=True,
        ),
        Column("ordinal", Integer(), nullable=False),
        Column("properties", postgresql.JSON(), nullable=False),
        Column("original_datasheet_id", postgresql.UUID(), nullable=False),
        Column("original_owner_organization_id", postgresql.UUID(), nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_index(
        op.f("ix_datasheet_element_abstract_element_id"),
        "datasheet_element",
        ["element_def_id"],
    )

    op.create_index(
        op.f("ix_datasheet_element_original_datasheet_id"),
        "datasheet_element",
        ["original_datasheet_id"],
    )


def create_report_tables():
    op.create_table(
        "report_definition",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("project_definition_id", postgresql.UUID(), nullable=False),
        Column("name", String, nullable=False),
        Column("structure", postgresql.JSON(), nullable=False),
        Column("distributable", Boolean, nullable=False),
    )

    op.create_table(
        "distributable_items",
        Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column(
            "report_definition_id", postgresql.UUID(), nullable=False, primary_key=True
        ),
        Column("node_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("supplied_item", postgresql.JSON(), nullable=False),
        Column("groups", postgresql.JSON(), nullable=False),
        Column("distributions", postgresql.JSON(), nullable=False),
        Column("summary", postgresql.JSON(), nullable=False),
        Column("columns", postgresql.JSON(), nullable=False),
        Column("name", String, nullable=False),
        Column("obsolete", Boolean, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "distribution",
        Column("id", postgresql.UUID(), nullable=False, primary_key=True),
        Column("file_url", String, nullable=False),
        Column("item_ids", ARRAY(postgresql.UUID(), dimensions=1), nullable=False),
        Column("state", String(32), nullable=False),
        Column("obsolete", Boolean, nullable=False),
        Column("creation_date_utc", DateTime(timezone=True), nullable=False),
    )


def upgrade():
    create_global_table()
    create_project_definition_tables()
    create_project_tables()
    create_datasheet_tables()
    create_report_tables()


def downgrade():
    pass
