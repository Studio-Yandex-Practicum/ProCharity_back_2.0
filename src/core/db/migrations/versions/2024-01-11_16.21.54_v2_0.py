"""v2.0

Revision ID: fe9ed9252c2b
Revises: 916fdcc6c52a
Create Date: 2024-01-11 16:21:54.364133

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fe9ed9252c2b"
down_revision = "916fdcc6c52a"
branch_labels = None
depends_on = None


def migrate_users_categories():
    users_categories = sa.table("users_categories", sa.column("telegram_id"), sa.column("user_id"))
    users = sa.table("users", sa.column("telegram_id"), sa.column("id"))
    (
        sa.update(users_categories)
        .values(user_id=users.c.id)
        .where(users_categories.c.telegram_id == users.c.telegram_id)
    )


def upgrade() -> None:
    op.drop_table("statistics")

    # Admin Token Request

    op.add_column(
        "admin_token_requests",
        sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.add_column(
        "admin_token_requests",
        sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.alter_column(
        "admin_token_requests",
        "token_expiration_date",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.Date(),
        existing_nullable=False,
    )

    # Categories

    op.alter_column(
        "categories", "archive", new_column_name="is_archived", server_default=sa.text("false"), nullable=False
    )
    op.add_column(
        "categories", sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.add_column(
        "categories", sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.alter_column("categories", "name", existing_type=sa.VARCHAR(length=100), nullable=False)

    # External Site User

    op.add_column(
        "external_site_users",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True, primary_key=True),
    )
    op.create_primary_key(None, "external_site_users", ["id"])
    op.alter_column(
        "external_site_users",
        "external_id",
        type_=sa.Integer(),
        nullable=True,
        index=True,
    )
    op.alter_column(
        "external_site_users",
        "external_id_hash",
        new_column_name="id_hash",
        type_=sa.String(length=256),
        nullable=True,
    )
    op.alter_column(
        "external_site_users",
        "updated_date",
        new_column_name="updated_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.alter_column(
        "external_site_users",
        "created_date",
        new_column_name="created_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.alter_column(
        "external_site_users",
        "specializations",
        existing_type=sa.VARCHAR(),
        type_=sa.ARRAY(sa.Integer()),
        existing_nullable=True,
        postgresql_using="string_to_array(external_site_users.specializations, ',')::integer[]",
    )
    op.alter_column("external_site_users", "email", existing_type=sa.VARCHAR(length=48), nullable=True)

    # Notification

    op.add_column(
        "notifications", sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.add_column(
        "notifications", sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.alter_column("notifications", "was_sent", existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column("notifications", "sent_date", existing_type=postgresql.TIMESTAMP(), type_=sa.Date(), nullable=False)
    op.alter_column("notifications", "sent_by", existing_type=sa.VARCHAR(length=48), nullable=False)

    # Task

    op.alter_column(
        "tasks",
        "updated_date",
        new_column_name="updated_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.alter_column(
        "tasks",
        "created_date",
        new_column_name="created_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.alter_column(
        "tasks",
        "archive",
        new_column_name="is_archived",
        type_=sa.Boolean(),
        server_default=sa.text("false"),
        nullable=False,
    )
    op.alter_column("tasks", "title", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("tasks", "category_id", existing_type=sa.INTEGER())
    op.alter_column("tasks", "bonus", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column("tasks", "location", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("tasks", "link", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("tasks", "description", existing_type=sa.VARCHAR(), nullable=False)

    # Unsubscribe Reason

    op.alter_column(
        "unsubscribe_reason",
        "updated_date",
        new_column_name="updated_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.alter_column(
        "unsubscribe_reason",
        "added_date",
        new_column_name="created_at",
        type_=sa.Date(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    op.add_column("unsubscribe_reason", sa.Column("user_id", sa.Integer()))
    op.add_column("unsubscribe_reason", sa.Column("unsubscribe_reason", sa.String(length=128), nullable=True))

    _users_categories = sa.table("unsubscribe_reason", sa.column("telegram_id"), sa.column("user_id"))
    users = sa.table("users", sa.column("telegram_id"), sa.column("id"))
    op.execute(
        (
            sa.update(_users_categories)
            .values(user_id=users.c.id)
            .where(_users_categories.c.telegram_id == users.c.telegram_id)
        )
    )

    op.drop_column("unsubscribe_reason", "archive")
    op.drop_column("unsubscribe_reason", "telegram_id")
    op.drop_column("unsubscribe_reason", "reason_canceling")

    op.drop_constraint("reasons_canceling_pkey", "unsubscribe_reason", type_="foreignkey")
    op.create_foreign_key("reasons_canceling_pkey", "unsubscribe_reason", "users", ["user_id"], ["id"])

    # User's Categories

    op.add_column("users_categories", sa.Column("user_id", sa.Integer()))
    op.add_column(
        "users_categories",
        sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.add_column(
        "users_categories",
        sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    users_categories = sa.table("users_categories", sa.column("telegram_id"), sa.column("user_id"))
    users = sa.table("users", sa.column("telegram_id"), sa.column("id"))
    op.execute(
        (
            sa.update(users_categories)
            .values(user_id=users.c.id)
            .where(users_categories.c.telegram_id == users.c.telegram_id)
        )
    )

    op.drop_constraint("users_categories_telegram_id_fkey", "users_categories", type_="foreignkey")
    op.create_foreign_key(None, "users_categories", "users", ["user_id"], ["id"])
    op.drop_column("users_categories", "telegram_id")

    # Some Queries for creating foreign keys.

    ## Dumps
    op.alter_column("users", "external_id", new_column_name="dump_id")
    op.add_column("users", sa.Column("external_id", sa.Integer(), nullable=True))
    op.create_foreign_key("users_external_id_fkey", "users", "external_site_users", ["external_id"], ["id"])

    op.execute(
        "INSERT INTO external_site_users (external_id) "
        "SELECT users.dump_id "
        "FROM users "
        "WHERE (users.dump_id NOT IN (SELECT external_site_users.external_id "
        "FROM external_site_users));"
    )
    op.execute(
        "UPDATE users "
        "SET external_id = subquery.ext_ref "
        "FROM ("
        "SELECT external_site_users.id as ext_ref, external_site_users.external_id as ext_id FROM external_site_users"
        ") as subquery "
        "WHERE users.external_id = subquery.ext_id;"
    )


def downgrade() -> None:
    raise NotImplementedError("Do not supported.")
