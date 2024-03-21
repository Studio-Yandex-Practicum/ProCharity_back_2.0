"""delete_category_insert_subcategory

Revision ID: 87c7d29e3ddb
Revises: 52647dd43d55
Create Date: 2022-10-22 13:27:10.144666

"""

from sqlalchemy import select

# from app.database import db_session
# from app.models import Users_Categories, Category


# revision identifiers, used by Alembic.
revision = "87c7d29e3ddb"
down_revision = "52647dd43d55"
branch_labels = None
depends_on = None


def upgrade():
    pass
    # users_child_category = db_session.execute(select(
    #     Users_Categories.telegram_id, Users_Categories.category_id
    # ).join(Category).where(
    #     Category.parent_id.is_not(None)
    # )).all()

    # users_child_category_dict = {}
    # for user_tg_id, user_category in users_child_category:
    #     users_child_category_dict.setdefault(user_tg_id, set()).add(user_category)

    # parent_categories = set(db_session.execute(select(Category).join(
    #     Users_Categories
    # ).where(
    #     Category.parent_id.is_(None)
    # )).scalars())

    # for parent_category in parent_categories:
    #     for child in parent_category.children:
    #         child_id = child.id
    #         for user in parent_category.users:
    #             user_id = user.telegram_id
    #             if user_id in users_child_category_dict and child_id in users_child_category_dict[user_id]:
    #                 continue
    #             subcategory = Users_Categories(telegram_id=user_id, category_id=child_id)
    #             db_session.add(subcategory)
    #     parent_category.users = []

    # db_session.commit()


def downgrade():
    pass
