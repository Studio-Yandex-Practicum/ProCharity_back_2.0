from pydantic import BaseModel


class FeedbackModel(BaseModel):
    """Класс модели для обратной связи."""

    telegram_id: int
    surname: str
    name: str
    email: str
    feedback: str

    def to_message(self):
        return f'''Recieved feedback from telegram bot user.
                telegram_id: {self.telegram_id},
                surname: {self.surname},
                name: {self.name},
                email: {self.email},
                feedback: {self.feedback}
                '''
