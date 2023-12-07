from pydantic import BaseModel


class FeedbackModel(BaseModel):
    """Класс модели для обратной связи."""

    surname: str
    name: str
    email: str
    feedback: str

    def to_message(self):
        return f"""Получено сообщение от пользователя телеграмм бота.
                Фамилия: {self.surname},
                Имя: {self.name},
                email: {self.email},
                Отзыв: {self.feedback}
                """
