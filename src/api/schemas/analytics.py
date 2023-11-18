from pydantic import BaseModel


class ActiveTasks(BaseModel):
    """Класс ответа для аналитики по задачам."""

    last_update: str
    active_tasks: int


class ReasonCancelingStatistics(BaseModel):
    to_much_messages: int = 0
    no_time: int = 0
    no_match: int = 0
    uncomfortable: int = 0
    funds_dont_choose: int = 0
    other: int = 0


class Analytic(BaseModel):
    """Класс модели запроса для статистики."""

    command_stats: dict[str, str] = {}
    reasons_canceling: ReasonCancelingStatistics = {}
    number_users: int = 0
    all_users_statistic: dict[str, str] = {}
    active_users_statistic: dict[str, str] = {}
    tasks: ActiveTasks = {}
