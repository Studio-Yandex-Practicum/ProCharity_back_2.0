"""stub

Revision ID: 916fdcc6c52a
Revises: 0e74b21e97f4
Create Date: 2024-01-11 16:14:36.031006

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "916fdcc6c52a"
down_revision = "0e74b21e97f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("reasons_canceling", "unsubscribe_reason")

    # User

    op.add_column(
        "users", sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.alter_column("users", "has_mailing", existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column(
        "users",
        "date_registration",
        new_column_name="created_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.alter_column(
        "users", "external_signup_date", existing_type=postgresql.TIMESTAMP(), type_=sa.Date(), existing_nullable=True
    )
    op.add_column(table_name="users", column=sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True))
    op.create_unique_constraint(constraint_name="users_telegram_id_key", table_name="users", columns=["telegram_id"])
    op.drop_constraint(constraint_name="users_categories_telegram_id_fkey", table_name="users_categories")
    op.drop_constraint(constraint_name="users_pkey", table_name="users")
    op.create_primary_key(constraint_name="users_pkey", table_name="users", columns=["id"])
    op.create_foreign_key(
        constraint_name="users_categories_telegram_id_fkey",
        source_table="users_categories",
        referent_table="users",
        local_cols=["telegram_id"],
        remote_cols=["telegram_id"],
    )

    # Admin User

    op.add_column("admin_users", sa.Column("last_login", sa.Date(), nullable=True))
    op.alter_column(
        "admin_users", "password", type_=sa.String(length=1024), nullable=False, new_column_name="hashed_password"
    )
    op.add_column("admin_users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("admin_users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("admin_users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column(
        "admin_users", sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.add_column(
        "admin_users", sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.alter_column(
        "admin_users",
        "email",
        existing_type=sa.VARCHAR(length=48),
        type_=sa.String(length=320),
        existing_nullable=False,
    )
    op.drop_constraint("admin_users_email_key", "admin_users", type_="unique")
    op.create_index(op.f("ix_admin_users_email"), "admin_users", ["email"], unique=True)
    op.drop_column("admin_users", "last_logon")


def downgrade() -> None:
    op.rename_table("unsubscribe_reason", "reasons_canceling")

    # User

    op.drop_constraint(constraint_name="users_categories_telegram_id_fkey", table_name="users_categories")
    op.drop_constraint(constraint_name="users_pkey", table_name="users")
    op.create_primary_key(constraint_name="users_pkey", table_name="users", columns=["telegram_id"])
    op.drop_constraint(constraint_name="users_telegram_id_key", table_name="users")
    op.create_foreign_key(
        constraint_name="users_categories_telegram_id_fkey",
        source_table="users_categories",
        referent_table="users",
        local_cols=["telegram_id"],
        remote_cols=["telegram_id"],
    )
    op.drop_column("users", "id")
    op.drop_column("users", "updated_at")
    op.alter_column("users", "has_mailing", existing_type=sa.Boolean(), nullable=False)
    op.alter_column(
        "users",
        "created_at",
        new_column_name="date_registration",
        type_=postgresql.TIMESTAMP(),
        autoincrement=False,
        nullable=False,
    )
    op.alter_column(
        "users", "external_signup_date", existing_type=sa.Date(), type_=postgresql.TIMESTAMP(), existing_nullable=True
    )

    # Admin User

    op.drop_column("admin_users", "last_login")
    op.drop_column("admin_users", "is_active")
    op.drop_column("admin_users", "is_superuser")
    op.drop_column("admin_users", "is_verified")
    op.drop_column("admin_users", "created_at")
    op.drop_column("admin_users", "updated_at")
    op.alter_column(
        "admin_users", "hashed_password", new_column_name="password", type_=sa.String(length=128), nullable=False
    )
    op.alter_column(
        "admin_users",
        "email",
        existing_type=sa.String(length=320),
        type_=sa.VARCHAR(length=48),
        nullable=False,
    )
    op.create_unique_constraint("admin_users_email_key", "admin_users", ["email"])
    op.drop_index(op.f("ix_admin_users_email"), "admin_users")
    op.add_column("admin_users", sa.Column("last_logon", sa.TIMESTAMP(), nullable=True))
