from enum import StrEnum


class TelegramNotificationUsersGroups(StrEnum):
    """Класс с доступными категориями пользователей,
    которым будет отправлено сообщение"""

    ALL = "all"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"

    def to_bool_or_none(self) -> bool | None:
        if self == self.__class__.SUBSCRIBED:
            return True
        if self == self.__class__.UNSUBSCRIBED:
            return False


class UserResponseAction(StrEnum):
    """Типы действий с откликом пользователя на задачу.

    - respond: создать отклик;
    - unrespond: удалить отклик.
    """

    RESPOND = "respond"
    UNRESPOND = "cancel_respond"


class UserRoles(StrEnum):
    """Роли пользователя в системе.

    Значения членов перечисления - строки длиной не более
    src.core.db.models.MAX_USER_ROLE_NAME_LENGTH.
    """

    FUND = "fund"
    VOLUNTEER = "volunteer"


class UserStatus(StrEnum):
    """Класс с доступными статусами модерации пользователей

    Расшифровки доступных статусов:

    - NEW_VOL: Новый волонтер
    - NEW_FUND: Новый фонд
    - WAIT: Ожидает модерации
    - MODERATED: Промодерирован
    - NO_MODERATED: Не прошел модерацию
    - BLOCKED: Заблокирован
    """

    NEW_VOL = "new"
    NEW_FUND = "new"
    WAIT = "wait"
    MODERATED = "moderated"
    NO_MODERATED = "no_moderated"
    BLOCKED = "blocked"


class UserRoleFilterValues(StrEnum):
    """Режимы фильтрации на основе поля role."""

    FUND = "fund"
    VOLUNTEER = "volunteer"
    UNKNOWN = "unknown"


class UserStatusFilterValues(StrEnum):
    """Режимы фильтрации на основе поля moderation_status."""

    NEW = "new"
    WAIT = "wait"
    MODERATED = "moderated"
    NO_MODERATED = "no_moderated"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"
