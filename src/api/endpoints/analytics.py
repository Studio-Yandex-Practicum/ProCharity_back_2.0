from fastapi import APIRouter, Depends

from src.api.schemas import Users
from src.api.services import TaskService
from src.api.services.messages import TelegramNotificationService

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает количество пользователей.")
async def get_users() -> Users:
    pass
