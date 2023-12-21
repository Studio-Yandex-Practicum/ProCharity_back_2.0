"""Change type of token_expiration_date

Revision ID: d55ce4851e71
Revises: 6583446a0d10
Create Date: 2023-12-21 18:26:20.856742

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d55ce4851e71"
down_revision = "6583446a0d10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "admin_token_requests",
        "token_expiration_date",
        existing_type=sa.DATE(),
        type_=sa.DateTime(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "admin_token_requests",
        "token_expiration_date",
        existing_type=sa.DateTime(),
        type_=sa.DATE(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
