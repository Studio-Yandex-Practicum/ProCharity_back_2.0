from enum import StrEnum


class TelegramNotificationUsersGroups(StrEnum):
    """Класс с доступными категориями пользователелей,
     которым будет отправлено сообщение"""
    ALL = "all"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
