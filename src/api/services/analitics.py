from src.core.db.db import get_session
from src.core.db.models import User


async def get_number_users_statistic():
    users = get_session.query(User.has_mailing, User.banned).all()
    number_users = len(users)
    return number_users
