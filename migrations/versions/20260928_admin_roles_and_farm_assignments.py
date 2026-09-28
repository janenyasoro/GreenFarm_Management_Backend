"""Reconcile GreenFarm schema and add admin/user assignment support.

The repository had no prior migration revision. Creating missing tables from the
current model metadata makes this initial revision usable on a clean database;
existing tables are left intact and receive only the missing admin columns.
Revision ID: 20260928_admin_roles
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = "20260928_admin_roles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    from models import db

    bind = op.get_bind()
    # Initial install: create all model tables. Existing deployments: create_all
    # leaves existing tables unchanged, after which this revision adds columns.
    db.metadata.create_all(bind=bind, checkfirst=True)
    inspector = sa.inspect(bind)

    if "farms" in inspector.get_table_names():
        farm_columns = {column["name"]: column for column in inspector.get_columns("farms")}
        if "owner_id" in farm_columns and not farm_columns["owner_id"]["nullable"]:
            with op.batch_alter_table("farms") as batch:
                batch.alter_column("owner_id", existing_type=farm_columns["owner_id"]["type"], nullable=True)
        if "is_active" not in farm_columns:
            with op.batch_alter_table("farms") as batch:
                batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
                batch.create_index("ix_farms_is_active", ["is_active"])

    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        user_columns = {column["name"]: column for column in inspector.get_columns("users")}
        if "farm_id" not in user_columns:
            with op.batch_alter_table("users") as batch:
                # Intentionally no FK: Farm.owner_id already points at User,
                # and a second FK would create a cyclic DDL dependency.
                batch.add_column(sa.Column("farm_id", sa.Integer(), nullable=True))
                batch.create_index("ix_users_farm_id", ["farm_id"])
    op.execute("UPDATE users SET role = CASE lower(role) WHEN 'admin' THEN 'ADMIN' WHEN 'owner' THEN 'FARM_OWNER' WHEN 'worker' THEN 'FARM_WORKER' ELSE role END")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    if "users" in tables:
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "farm_id" in columns:
            with op.batch_alter_table("users") as batch:
                batch.drop_index("ix_users_farm_id")
                batch.drop_column("farm_id")
        op.execute("UPDATE users SET role = CASE role WHEN 'ADMIN' THEN 'admin' WHEN 'FARM_OWNER' THEN 'owner' WHEN 'FARM_WORKER' THEN 'worker' ELSE role END")
    inspector = sa.inspect(bind)
    if "farms" in inspector.get_table_names():
        columns = {column["name"]: column for column in inspector.get_columns("farms")}
        if "is_active" in columns:
            with op.batch_alter_table("farms") as batch:
                batch.drop_index("ix_farms_is_active")
                batch.drop_column("is_active")
        if "owner_id" in columns and columns["owner_id"]["nullable"]:
            with op.batch_alter_table("farms") as batch:
                batch.alter_column("owner_id", existing_type=columns["owner_id"]["type"], nullable=False)
