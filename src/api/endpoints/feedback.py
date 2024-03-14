from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import FeedbackSchema
from src.core.depends.container import Container
from src.core.services.email import EmailProvider

feedback_router = APIRouter()


@feedback_router.post("")
@inject
async def web_app_data_handler(
    feedback: FeedbackSchema,
    email_admin: str = Depends(Provide[Container.settings.provided.EMAIL_ADMIN]),
    email_provider: EmailProvider = Depends(Provide[Container.core_services_container.email_provider]),
):
    await email_provider.send_question(
        external_id=feedback.external_id,
        telegram_link=feedback.telegram_link,
        name=feedback.name,
        from_email=feedback.email,
        message=feedback.message,
        to_email=email_admin,
    )
