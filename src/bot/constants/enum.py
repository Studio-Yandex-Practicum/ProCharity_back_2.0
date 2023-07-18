import enum


class REASONS(enum.StrEnum):
    to_much_messages = "Слишком много уведомлений"
    no_time = "Нет времени на волонтёрство"
    no_match = "Нет подходящих заданий"
    uncomfortable = "Бот мне неудобен"
    funds_dont_choose = "Фонды меня не выбирают"
    other = "Другое"
