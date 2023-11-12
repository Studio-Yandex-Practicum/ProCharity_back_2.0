from pydantic import BaseModel


class Analytic(BaseModel):
    """Класс модели запроса для статистики."""

    command_stats: dict[str, str] = {}
    reasons_canceling: str = ""
    number_users: int = 0
    all_users_statistic: dict[str, str] = {}
    active_users_statistic: dict[str, str] = {}
    tasks: dict[str, str] = {}
