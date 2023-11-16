"""initial

Revision ID: 6c4739908b74
Revises:
Create Date: 2023-11-09 14:46:01.346164

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6c4739908b74"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("telegram_id", sa.BigInteger(), nullable=False),
            sa.Column("username", sa.String(length=32), nullable=True),
            sa.Column("email", sa.String(length=48), nullable=True),
            sa.Column("external_id", sa.Integer(), nullable=True),
            sa.Column("first_name", sa.String(length=64), nullable=True),
            sa.Column("last_name", sa.String(length=64), nullable=True),
            sa.Column("has_mailing", sa.Boolean(), nullable=False),
            sa.Column("external_signup_date", sa.Date(), nullable=True),
            sa.Column("banned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
            sa.UniqueConstraint("external_id"),
            sa.UniqueConstraint("telegram_id"),
            sa.UniqueConstraint("username"),
        )
    else:
        op.alter_column("users", "date_registration", new_column_name="created_at")
        op.add_column(
            "users", sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
        )
        op.add_column("users", sa.Column("id", sa.Integer()))
        op.execute("CREATE SEQUENCE users_id_seq")
        op.execute("UPDATE users SET id = nextval('users_id_seq')")
        op.alter_column("users", "id", nullable=False)
        op.create_unique_constraint("users_id_key", "users", ["id"])

    if not inspector.has_table("admin_users"):
        op.create_table(
            "admin_users",
            sa.Column("email", sa.String(length=48), nullable=False),
            sa.Column("first_name", sa.String(length=64), nullable=True),
            sa.Column("last_name", sa.String(length=64), nullable=True),
            sa.Column("password", sa.String(length=128), nullable=False),
            sa.Column("last_login", sa.Date(), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
    else:
        op.add_column(
            "admin_users",
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.add_column(
            "admin_users",
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.alter_column("admin_users", "last_logon", new_column_name="last_login")

    if not inspector.has_table("categories"):
        op.create_table(
            "categories",
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("parent_id", sa.Integer(), nullable=True),
            sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(
                ["parent_id"],
                ["categories.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        op.add_column(
            "categories",
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.add_column(
            "categories",
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.alter_column("categories", "archive", new_column_name="is_archived")

    if not inspector.has_table("external_site_users"):
        op.create_table(
            "external_site_users",
            sa.Column("id_hash", sa.String(length=256), nullable=False),
            sa.Column("email", sa.String(length=48), nullable=False),
            sa.Column("first_name", sa.String(length=64), nullable=True),
            sa.Column("last_name", sa.String(length=64), nullable=True),
            sa.Column("specializations", sa.ARRAY(sa.Integer()), nullable=True),
            sa.Column("source", sa.String(), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
    else:
        op.alter_column("external_site_users", "external_id", new_column_name="id")
        op.alter_column("external_site_users", "external_id_hash", new_column_name="id_hash")
        op.alter_column("external_site_users", "created_date", new_column_name="created_at")
        op.alter_column("external_site_users", "updated_date", new_column_name="updated_at")

    if not inspector.has_table("notifications"):
        op.create_table(
            "notifications",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("message", sa.String(length=4096), nullable=False),
            sa.Column("was_sent", sa.Boolean()),
            sa.Column("sent_date", sa.TIMESTAMP()),
            sa.Column("sent_by", sa.String(length=48)),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        op.add_column(
            "notifications",
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.add_column(
            "notifications",
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    if not inspector.has_table("reasons_canceling") and not inspector.has_table("unsubscribe_reason"):
        op.create_table(
            "unsubscribe_reason",
            sa.Column("id", sa.Integer(), unique=True, nullable=False),
            sa.Column("telegram_id", sa.BigInteger(), nullable=True),
            sa.Column("unsubscribe_reason", sa.String(length=48), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
            sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
            sa.Column("archive", sa.Boolean(), nullable=True, server_default=sa.sql.expression.false()),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        op.rename_table("reasons_canceling", "unsubscribe_reason")
        op.alter_column("unsubscribe_reason", "reason_canceling", new_column_name="unsubscribe_reason")
        op.alter_column("unsubscribe_reason", "added_date", new_column_name="created_at")
        op.alter_column("unsubscribe_reason", "updated_date", new_column_name="updated_at")
        op.add_column(
            "unsubscribe_reason", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True)
        )

    if not inspector.has_table("tasks"):
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(), nullable=True),
            sa.Column("name_organization", sa.String(), nullable=True),
            sa.Column("deadline", sa.Date(), nullable=True),
            sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id")),
            sa.Column("bonus", sa.Integer()),
            sa.Column("location", sa.String()),
            sa.Column("link", sa.String()),
            sa.Column("description", sa.String()),
            sa.Column("is_archived", sa.Boolean(), nullable=True, server_default=sa.sql.expression.false()),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
            sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
        )
    else:
        op.alter_column("tasks", "created_date", new_column_name="created_at")
        op.alter_column("tasks", "updated_date", new_column_name="updated_at")
        op.alter_column("tasks", "archive", new_column_name="is_archived")

    if not inspector.has_table("users_categories"):
        op.create_table(
            "users_categories",
            sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
            sa.Column("telegram_id", sa.BigInteger()),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
            sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
        )
    else:
        op.add_column("users_categories", sa.Column("user_id", sa.Integer()))
        op.execute(
            "UPDATE users_categories SET user_id = users.id FROM users WHERE users_categories.telegram_id = users.telegram_id"
        )
        op.create_foreign_key("users_categories_user_id_fkey", "users_categories", "users", ["user_id"], ["id"])
        op.drop_constraint("users_categories_telegram_id_fkey", "users_categories", type_="foreignkey")
        op.drop_constraint("users_pkey", "users", type_="primary")
        op.create_primary_key("users_pkey", "users", ["id"])
        op.add_column(
            "users_categories",
            sa.Column("created_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.add_column(
            "users_categories",
            sa.Column("updated_at", sa.Date(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_categories")
    op.drop_table("unsubscribe_reason")
    op.drop_table("tasks")
    op.drop_table("users")
    op.drop_table("external_site_users")
    op.drop_table("categories")
    op.drop_table("admin_users")
    op.drop_table("admin_token_requests")
    # ### end Alembic commands ###
