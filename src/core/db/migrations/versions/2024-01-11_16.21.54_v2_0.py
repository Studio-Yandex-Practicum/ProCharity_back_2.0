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
    try:
        from src.core.db.models import User, UsersCategories
    except ImportError:
        return
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

    op.alter_column(
        "external_site_users",
        "external_id",
        new_column_name="id",
        type_=sa.Integer(),
        autoincrement=True,
        nullable=False,
    )
    op.alter_column(
        "external_site_users",
        "external_id_hash",
        new_column_name="id_hash",
        type_=sa.String(length=256),
        nullable=False,
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

    op.create_foreign_key(None, "unsubscribe_reason", "users", ["user_id"], ["id"])

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


def downgrade() -> None:
    op.create_table(
        "statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.Integer(), nullable=True),
        sa.Column("command", sa.String(length=100), nullable=True),
        sa.Column("added_date", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Admin Token Request

    op.drop_column("admin_token_requests", "created_at")
    op.drop_column("admin_token_requests", "updated_at")
    op.alter_column(
        "admin_token_requests",
        "token_expiration_date",
        existing_type=sa.Date(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )

    # Categories

    op.alter_column("categories", "is_archived", new_column_name="archive", server_default=None, nullable=True)
    op.drop_column("categories", "created_at")
    op.drop_column("categories", "updated_at")
    op.alter_column("categories", "name", existing_type=sa.VARCHAR(length=100), nullable=True)

    # External Site User

    op.alter_column(
        "external_site_users",
        "id",
        new_column_name="external_id",
        type_=sa.String(length=256),
        nullable=True,
    )
    op.alter_column(
        "external_site_users",
        "id_hash",
        new_column_name="external_id_hash",
        type_=sa.String(length=256),
        nullable=True,
    )
    op.alter_column(
        "external_site_users",
        "updated_at",
        new_column_name="updated_date",
        type_=postgresql.TIMESTAMP(),
        server_default=None,
        nullable=True,
    )
    op.alter_column(
        "external_site_users",
        "created_at",
        new_column_name="created_date",
        type_=postgresql.TIMESTAMP(),
        server_default=None,
        nullable=True,
    )
    op.alter_column(
        "external_site_users",
        "specializations",
        existing_type=sa.ARRAY(sa.Integer()),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="array_to_string(external_site_users.specializations, ',')",
    )

    # Notification

    op.drop_column("notifications", "created_at")
    op.drop_column("notifications", "updated_at")
    op.alter_column("notifications", "was_sent", existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column("notifications", "sent_date", existing_type=sa.Date(), type_=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column("notifications", "sent_by", existing_type=sa.VARCHAR(length=48), nullable=True)

    # Task

    op.alter_column(
        "tasks",
        "updated_at",
        new_column_name="updated_date",
        type_=postgresql.TIMESTAMP(),
        server_default=None,
        nullable=True,
    )
    op.alter_column(
        "tasks",
        "created_at",
        new_column_name="created_date",
        type_=postgresql.TIMESTAMP(),
        server_default=None,
        nullable=True,
    )
    op.alter_column(
        "tasks",
        "is_archived",
        new_column_name="archive",
        type_=sa.Boolean(),
        server_default=None,
        nullable=True,
    )
    op.alter_column("tasks", "title", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("tasks", "category_id", existing_type=sa.INTEGER())
    op.alter_column("tasks", "bonus", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("tasks", "location", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("tasks", "link", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("tasks", "description", existing_type=sa.VARCHAR(), nullable=True)

    # Unsubscribe Reason

    op.drop_constraint(None, "unsubscribe_reason", type_="foreignkey")
    op.add_column(
        "unsubscribe_reason", sa.Column("archive", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )
    op.add_column("unsubscribe_reason", sa.Column("telegram_id", sa.String(length=255), nullable=False))
    op.add_column("unsubscribe_reason", sa.Column("reason_canceling", sa.String(length=255), nullable=False))

    _users_categories = sa.table("unsubscribe_reason", sa.column("telegram_id"), sa.column("user_id"))
    users = sa.table("users", sa.column("telegram_id"), sa.column("id"))
    op.execute(
        (
            sa.update(_users_categories)
            .values(user_id=users.c.id)
            .where(_users_categories.c.telegram_id == users.c.telegram_id)
        )
    )

    op.drop_column("unsubscribe_reason", "user_id")
    op.drop_column("unsubscribe_reason", "unsubscribe_reason")
    op.alter_column(
        "unsubscribe_reason",
        "updated_at",
        new_column_name="updated_date",
        type_=postgresql.TIMESTAMP(),
        server_default=None,
        nullable=True,
    )
    op.alter_column(
        "unsubscribe_reason",
        "created_at",
        new_column_name="added_date",
        type_=postgresql.TIMESTAMP(),
        server_default=None,
        nullable=True,
    )

    # User's Categories

    op.add_column("users_categories", sa.Column("telegram_id", sa.String(length=255), nullable=False))

    _users_categories = sa.table("users_categories", sa.column("telegram_id"), sa.column("user_id"))
    users = sa.table("users", sa.column("telegram_id"), sa.column("id"))
    op.execute(
        (
            sa.update(_users_categories)
            .values(telegram_id=users.c.telegram_id)
            .where(_users_categories.c.user_id == users.c.id)
        )
    )

    op.drop_constraint(None, "users_categories", type_="foreignkey")
    op.create_foreign_key("users_categories_telegram_id_fkey", "users_categories", "users", ["telegram_id"], ["id"])
    op.drop_column("users_categories", "updated_at")
    op.drop_column("users_categories", "created_at")
    op.drop_column("users_categories", "user_id")
