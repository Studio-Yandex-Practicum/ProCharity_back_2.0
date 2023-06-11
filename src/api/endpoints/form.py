from typing import Iterator

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse

from src.api.schemas import FeedbackFormQueryParams
from src.settings import settings

api_router = APIRouter()


@api_router.get(
    "/feedback-form",
    status_code=status.HTTP_200_OK,
    summary="Вернуть шаблон формы обратной связи в телеграм",
    response_description="Предоставить пользователю форму для заполнения",
)
async def user_register_form_webhook(
    request: Request,
    parameters: FeedbackFormQueryParams = Depends(FeedbackFormQueryParams),
) -> StreamingResponse:
    """
    Вернуть пользователю в телеграм форму для заполнения персональных данных.

    - **surname**: фамилия пользователя
    - **name**: имя пользователя
    - **email**: Email
    - **question**: вопрос или предложение
    """
    headers: dict[str, str] = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    def get_feedback_form() -> Iterator[bytes]:
        """
        Открывает для чтения html-шаблон формы регистрации пользователя.
        Возвращает генератор для последующего рендеринга шаблона StreamingResponse-ом.
        """
        with open(settings.feedback_form_template, "rb") as html_form:
            yield from html_form

    return StreamingResponse(get_feedback_form(), media_type="text/html", headers=headers)
