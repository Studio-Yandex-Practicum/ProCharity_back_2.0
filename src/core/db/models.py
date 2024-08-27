from datetime import date, datetime
from typing import Never

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from passlib.context import CryptContext
from sqlalchemy import ARRAY, BigInteger, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, backref, mapped_column, relationship
from sqlalchemy.sql import expression, func

from src.core.enums import UserRoles

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_USER_ROLE_NAME_LENGTH = 20
MAX_LENGTH_BOT_MESSAGE = 4096


class Base(DeclarativeBase):
    """Основа для базового класса."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __name__: Mapped[str]

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class ArchivableBase(AbstractConcreteBase, Base):
    """Базовый класс для данных, которые можно заархивировать."""

    is_archived: Mapped[bool] = mapped_column(server_default=expression.false())


class UsersCategories(Base):
    """Модель отношений пользователь-категория."""

    __tablename__ = "users_categories"

    id = None
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    def __repr__(self):
        return f"<User {self.user_id} - Category {self.category_id}>"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    role: Mapped[str] = mapped_column(String(MAX_USER_ROLE_NAME_LENGTH), nullable=True)
    username: Mapped[str | None] = mapped_column(String(256), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    has_mailing: Mapped[bool] = mapped_column(default=False)
    external_signup_date: Mapped[date | None] = mapped_column(nullable=True)
    banned: Mapped[bool] = mapped_column(server_default=expression.false())

    categories: Mapped[list["Category"]] = relationship(secondary="users_categories", back_populates="users")
    unsubscribe_reason: Mapped["UnsubscribeReason"] = relationship(back_populates="user")

    external_id: Mapped[int | None] = mapped_column(ForeignKey("external_site_users.id"), nullable=True)
    external_user: Mapped["ExternalSiteUser"] = relationship(back_populates="user")

    @property
    def is_volunteer(self) -> bool:
        return self.role == UserRoles.VOLUNTEER

    @property
    def telegram_link(self) -> str | None:
        base_url = "https://t.me/"
        if self.username:
            return base_url + self.username

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name or self.last_name or self.username:
            return self.first_name or self.last_name or self.username or Never
        return "Имя не известно"

    def __repr__(self):
        return f"<User {self.telegram_id}>"


class ExternalSiteUser(ArchivableBase):
    """Модель пользователя с сайта ProCharity."""

    __tablename__ = "external_site_users"

    id_hash: Mapped[str] = mapped_column(String(256), nullable=True)
    external_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(MAX_USER_ROLE_NAME_LENGTH), nullable=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    specializations: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    source: Mapped[str | None] = mapped_column(nullable=True)
    moderation_status: Mapped[str] = mapped_column(nullable=True)
    user: Mapped["User | None"] = relationship(back_populates="external_user", lazy="joined")
    task_responses: Mapped[list["Task"]] = relationship(
        secondary="task_response_volunteer", back_populates="responded_volunteers"
    )
    has_mailing_new_tasks: Mapped[bool] = mapped_column(nullable=True)
    has_mailing_profile: Mapped[bool] = mapped_column(nullable=True)
    has_mailing_my_tasks: Mapped[bool] = mapped_column(nullable=True)
    has_mailing_procharity: Mapped[bool] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<SiteUser {self.id}>"


class Task(ArchivableBase):
    """Модель задач."""

    __tablename__ = "tasks"

    title: Mapped[str]
    name_organization: Mapped[str] = mapped_column(nullable=True)
    legal_address: Mapped[str] = mapped_column(nullable=True)
    fund_city: Mapped[str] = mapped_column(nullable=True)
    fund_rating: Mapped[float] = mapped_column(nullable=True)
    fund_site: Mapped[str] = mapped_column(nullable=True)
    fund_link: Mapped[str] = mapped_column(nullable=True)
    yb_link: Mapped[str] = mapped_column(nullable=True)
    vk_link: Mapped[str] = mapped_column(nullable=True)
    fund_sections: Mapped[str] = mapped_column(nullable=True)

    deadline: Mapped[date] = mapped_column(nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category | None"] = relationship(back_populates="tasks")
    responded_volunteers: Mapped[list["ExternalSiteUser"]] = relationship(
        secondary="task_response_volunteer", back_populates="task_responses"
    )

    bonus: Mapped[int]
    location: Mapped[str]
    link: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    description_main: Mapped[list[dict]] = mapped_column(nullable=True, type_=JSONB)
    description_links: Mapped[list[dict]] = mapped_column(nullable=True, type_=JSONB)
    description_files: Mapped[list[dict]] = mapped_column(nullable=True, type_=JSONB)
    description_bonus: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<Task {self.title}>"


class Category(ArchivableBase):
    """Модель категорий."""

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(256))
    users: Mapped[list["User"]] = relationship(secondary="users_categories", back_populates="categories")
    tasks: Mapped[list["Task"]] = relationship(back_populates="category")
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    children: Mapped["Category"] = relationship(backref=backref("parent", remote_side="Category.id"))

    def __repr__(self):
        return f"<Category {self.name}>"


class AdminUser(SQLAlchemyBaseUserTable[int], Base):
    """Модель Админа."""

    __tablename__ = "admin_users"

    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_login: Mapped[date] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<Admin User {self.first_name} {self.last_name}>"


class AdminTokenRequest(Base):
    """Модель запрос токена."""

    __tablename__ = "admin_token_requests"

    email: Mapped[str] = mapped_column(String(48))
    is_superuser: Mapped[bool] = mapped_column(server_default=expression.false())
    token: Mapped[str] = mapped_column(String(128))
    token_expiration_date: Mapped[datetime]

    def __repr__(self):
        return f"<Register {self.email}>"


class UnsubscribeReason(Base):
    """Модель перечня обоснований отказа от подписки."""

    __tablename__ = "unsubscribe_reason"

    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="unsubscribe_reason")
    unsubscribe_reason: Mapped[str] = mapped_column(String(128), nullable=True)

    def __repr__(self):
        return f"<Unsubscribe reason: {self.unsubscribe_reason} for user {self.user}>"


class Notification(Base):
    """Модель уведомления."""

    __tablename__ = "notifications"

    message: Mapped[str] = mapped_column(String(length=4096), nullable=False)
    was_sent: Mapped[bool] = mapped_column(server_default=expression.false())
    sent_date: Mapped[date]
    sent_by: Mapped[str] = mapped_column(String(length=48))

    def __repr__(self):
        return f"<Notifications {self.message}>"


class TaskResponseVolunteer(Base):
    """Модель откликов волонтеров."""

    __tablename__ = "task_response_volunteer"

    id = None
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    external_site_user_id: Mapped[int] = mapped_column(ForeignKey("external_site_users.id"), primary_key=True)

    def __repr__(self):
        return f"<Response - Task {self.task_id} - Volunteer {self.external_site_user_id}>"


class TechMessage(ArchivableBase):
    """Модель для хранения технических сообщений для админов бота."""

    __tablename__ = "tech_messages"

    text: Mapped[str] = mapped_column(String(length=MAX_LENGTH_BOT_MESSAGE))
    was_read: Mapped[bool] = mapped_column(server_default=expression.false())

    def __repr__(self):
        return f"<Tech message - Text {self.text} - Was read {self.was_read}>"
