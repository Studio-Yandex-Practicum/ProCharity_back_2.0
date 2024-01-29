from datetime import date

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from passlib.context import CryptContext
from sqlalchemy import ARRAY, BigInteger, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, backref, mapped_column, relationship
from sqlalchemy.sql import expression, func

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Base(DeclarativeBase):
    """Основа для базового класса."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[date] = mapped_column(server_default=func.current_timestamp())
    updated_at: Mapped[date] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __name__: Mapped[str]


class ContentBase(AbstractConcreteBase, Base):
    """Базовый класс для контента (категорий и задач)."""

    is_archived: Mapped[bool] = mapped_column(server_default=expression.false())


class UsersCategories(Base):
    """Модель отношений пользователь-категория."""

    __tablename__ = "users_categories"

    id = None
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    def __repr__(self):
        return f"<User {self.user_id} - Category {self.category_id}>"


class FundsCategories(Base):
    """Модель отношений сферы деятельности фонда-категория."""

    __tablename__ = "funds_categories"

    id = None
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), primary_key=True)

    def __repr__(self):
        return f"<User {self.fund_id} - Category {self.category_id}>"


class Fund(Base):
    """Модель Фонд."""

    __tablename__ = "funds"

    name_organization: Mapped[str] = mapped_column(String, nullable=True)
    fund_city: Mapped[str] = mapped_column(String, nullable=True)
    fund_rating: Mapped[float] = mapped_column(Float, nullable=True)
    fund_site: Mapped[str] = mapped_column(String, nullable=True)
    yb_link: Mapped[str] = mapped_column(String, nullable=True)
    vk_link: Mapped[str] = mapped_column(String, nullable=True)
    fund_sections: Mapped[list["Category"]] = relationship(
        "Category", secondary="funds_categories", back_populates="funds"
    )

    def __repr__(self):
        return f"<Fund {self.name_organization}>"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(48), unique=True, nullable=True)
    external_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    has_mailing: Mapped[bool] = mapped_column(default=False)
    external_signup_date: Mapped[date] = mapped_column(nullable=True)
    banned: Mapped[bool] = mapped_column(server_default=expression.false())

    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary="users_categories", back_populates="users"
    )
    unsubscribe_reason: Mapped["UnsubscribeReason"] = relationship("UnsubscribeReason", back_populates="user")

    def __repr__(self):
        return f"<User {self.telegram_id}>"


class ExternalSiteUser(Base):
    """Модель пользователя с сайта ProCharity."""

    __tablename__ = "external_site_users"

    id_hash: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(48), unique=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    specializations: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    source: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<SiteUser {self.id}>"


class Task(ContentBase):
    """Модель задач."""

    __tablename__ = "tasks"

    title: Mapped[str]
    name_organization: Mapped[str] = mapped_column(String, nullable=True)
    fund_city: Mapped[str] = mapped_column(String, nullable=True)
    fund_rating: Mapped[float] = mapped_column(Float, nullable=True)
    fund_site: Mapped[str] = mapped_column(String, nullable=True)
    yb_link: Mapped[str] = mapped_column(String, nullable=True)
    vk_link: Mapped[str] = mapped_column(String, nullable=True)
    fund_sections: Mapped[list["Category"]] = relationship(
        "Category", secondary="funds_categories", back_populates="fund_obj"
    )

    deadline: Mapped[date] = mapped_column(nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped["Category | None"] = relationship(back_populates="tasks")

    bonus: Mapped[int]
    location: Mapped[str]
    link: Mapped[str]
    description: Mapped[str]

    def __repr__(self):
        return f"<Task {self.title}>"


class Category(ContentBase):
    """Модель категорий."""

    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(100))

    users: Mapped[list["User"]] = relationship("User", secondary="users_categories", back_populates="categories")

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")

    funds: Mapped[list["Fund"]] = relationship("Fund", secondary="funds_categories", back_populates="fund_sections")

    fund_obj: Mapped[list["Task"]] = relationship("Task", secondary="funds_categories", back_populates="fund_sections")

    parent_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    children: Mapped["Category"] = relationship("Category", backref=backref("parent", remote_side="Category.id"))

    def __repr__(self):
        return f"<Category {self.name}>"


class AdminUser(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "admin_users"

    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_login: Mapped[date] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<Admin User {self.first_name} {self.last_name}>"


class AdminTokenRequest(Base):
    __tablename__ = "admin_token_requests"

    email: Mapped[str] = mapped_column(String(48))
    token: Mapped[str] = mapped_column(String(128))
    token_expiration_date: Mapped[date]

    def __repr__(self):
        return f"<Register {self.email}>"


class UnsubscribeReason(Base):
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
