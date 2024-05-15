from urllib.parse import urljoin

from telegram import WebAppInfo

from src.bot.schemas import FeedbackFormQueryParams, TaskInfoPageQueryParams
from src.core.db.models import Task, User
from src.settings import settings


def get_feedback_web_app_info(user: User) -> WebAppInfo:
    """WebApp с формой обратной связи."""
    return WebAppInfo(
        url=urljoin(
            settings.feedback_form_template_url,
            FeedbackFormQueryParams(
                external_id=user.external_user.external_id if user.external_user else None,
                telegram_link=user.telegram_link,
                name=user.first_name,
                surname=user.last_name,
                email=getattr(user, "email", None),
            ).as_url_query(),
        )
    )


def get_task_web_app_info(task: Task) -> WebAppInfo:
    """WebApp для отображения подробной информации о задании и фонде."""
    query_params = TaskInfoPageQueryParams(
        id=task.id,
        api_root_path=settings.ROOT_PATH,
    )
    return WebAppInfo(
        url=urljoin(
            settings.task_info_page_template_url,
            query_params.as_url_query(),
        )
    )
