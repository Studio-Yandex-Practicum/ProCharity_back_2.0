"""add user.last_interaction

Revision ID: f4524481b9dc
Revises: b155a83b9476
Create Date: 2024-09-22 16:01:34.651499

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f4524481b9dc"
down_revision = "b155a83b9476"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("external_site_users", sa.Column("last_interaction", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("last_interaction", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "last_interaction")
    op.drop_column("external_site_users", "last_interaction")
    # ### end Alembic commands ###
