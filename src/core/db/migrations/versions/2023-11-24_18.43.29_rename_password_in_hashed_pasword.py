"""rename password in hashed_pasword

Revision ID: efd08301014a
Revises: 6c4739908b74
Create Date: 2023-11-24 18:43:29.141884

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "efd08301014a"
down_revision = "6c4739908b74"
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    bind = op.get_context().bind
    insp = sa.inspect(bind)
    columns = insp.get_columns(table_name)
    return any(c["name"] == column_name for c in columns)


def upgrade() -> None:
    if column_exists("admin_users", "password"):
        op.alter_column("admin_users", "password", new_column_name="hashed_password")

    if not column_exists("admin_users", "is_superuser"):
        op.add_column(
            "admin_users", sa.Column("is_superuser", sa.Boolean(), server_default='false', nullable=False)
        )
        op.add_column(
            "admin_users", sa.Column("is_verified", sa.Boolean(), server_default='false', nullable=False)
        )
        op.add_column(
            "admin_users", sa.Column("is_active", sa.Boolean(), server_default='false', nullable=False)
        )


def downgrade() -> None:
    if column_exists("admin_users", "hashed_password"):
        op.alter_column("admin_users", "hashed_password", new_column_name="password")
