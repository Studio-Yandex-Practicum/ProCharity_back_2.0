from dependency_injector.wiring import Provide

from src.core.db.models import Task
from src.core.depends.container import Container

TASK_DEADLINE_FORMAT = "%d.%m.%y"


def display_task(
    task: Task,
    updated_task: bool = False,
    bonus_info_url: str = Provide[Container.settings.provided.procharity_bonus_info_url],
) -> str:
    deadline = task.deadline.strftime(TASK_DEADLINE_FORMAT) if task.deadline else "Не указан."
    deadline_exclamation = "❗️" if updated_task else ""
    return (
        f"<b>Фонд:</b> {task.name_organization}\n\n"
        f"<b>Категория:</b> {task.category.name if task.category else 'Не указана.'}\n\n"
        f"{deadline_exclamation}<b>Срок:</b> {deadline}\n\n"
        f"<a href='{bonus_info_url}'><b>Бонусы:</b></a> {task.bonus} × 💎\n\n"
        f"<b>{task.title}\n\n</b>"
    )
