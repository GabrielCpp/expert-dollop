"""Add project definition plugin

Revision ID: 3ca73ea7f05a
Revises: 2c47a3dd1b88
Create Date: 2020-12-21 14:29:53.552830

"""
import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Boolean, DateTime, Column, Binary, Text
from alembic import op


# revision identifiers, used by Alembic.
revision = '3ca73ea7f05a'
down_revision = '2c47a3dd1b88'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_definition_plugin",
        Column('id', postgresql.UUID(), nullable=False, primary_key=True),
        Column('validation_schema', postgresql.JSON(), nullable=False),
        Column('default_config', postgresql.JSON(), nullable=False),
        Column('form_config', postgresql.JSON(), nullable=False),
        Column('name', String, nullable=False),
    )

    op.add_column(
        'project_definition',
        Column('plugins', ARRAY(postgresql.UUID(), dimensions=1), nullable=False)
    )


def downgrade():
    pass
