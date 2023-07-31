from fastapi import APIRouter, Depends

from src.api.schemas import Users
from src.api.services import TaskService
from src.api.services.messages import TelegramNotificationService

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает количество пользователей.")
async def get_users(
    tasks: list[TaskRequest],
    task_service: TaskService = Depends(),
    telegram_notification_service: TelegramNotificationService = Depends(),
) -> Users:
    pass
    # users = db_session.query(User.has_mailing, User.banned).all()
    # number_users = len(users)
    # # user[0] - has_mailing, user[1] - banned
    # subscribed_users = len([user for user in users if user[0] and not user[1]])
    # not_subscribed_users = len([user for user in users if not user[0] and not user[1]])
    # banned_users = len([user for user in users if user[1]])
    # return Users
