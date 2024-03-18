from pydantic import BaseModel


class FeedbackSchema(BaseModel):
    """Класс модели для обратной связи."""

    telegram_link: str | None
    external_id: str | None
    surname: str | None
    name: str
    email: str
    message: str
