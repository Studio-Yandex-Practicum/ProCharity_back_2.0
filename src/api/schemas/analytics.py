from pydantic import BaseModel


class ActiveTasks(BaseModel):
    """Класс ответа для аналитики по задачам."""

    last_update: str
    active_tasks: int


class Analytic(BaseModel):
    """Класс модели запроса для статистики."""

    command_stats: dict[str, str] = {}
    reasons_canceling: str = ""
    number_users: int = 0
    all_users_statistic: dict[str, str] = {}
    active_users_statistic: dict[str, str] = {}
    tasks: ActiveTasks = {}
