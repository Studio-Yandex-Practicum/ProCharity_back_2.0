import enum


class REASONS(enum.StrEnum):
    to_much_messages = "Слишком много уведомлений"
    no_time = "Нет времени на волонтерство"
    no_match = "Нет подходящих заданий"
    uncomfortable = "Неудобно пользоваться ботом"
    other = "Другое"


class CANCEL_RESPOND_REASONS(enum.StrEnum):
    no_feedback = "Представитель фонда не реагирует на отклик"
    no_time = "Взял в работу уже другие задания"
    by_mistake = "Оставил отклик на задание по ошибке"
    other = "Другое"
