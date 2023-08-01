from datetime import date
from typing import Optional

from sqlalchemy import ARRAY, BigInteger, ForeignKey, String, Integer
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, backref, mapped_column, relationship
from sqlalchemy.sql import expression, func


class Base(DeclarativeBase):
    """Основа для базового класса."""

    id: Mapped[int] = mapped_column(primary_key=True)
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

    def __repr__(self):
        return f"<User {self.telegram_id}>"


class ExternalSiteUser(Base):
    """Модель пользователя с сайта ProCharity."""

    __tablename__ = "external_site_users"

    id_hash: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(48), unique=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    specializations: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    source: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<SiteUser {self.id}>"


class Task(ContentBase):
    """Модель задач."""

    __tablename__ = "tasks"
    title: Mapped[str]
    name_organization: Mapped[str] = mapped_column(nullable=True)
    deadline: Mapped[date] = mapped_column(nullable=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="tasks")

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

    parent_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    children: Mapped["Category"] = relationship("Category", backref=backref("parent", remote_side="Category.id"))

    def __repr__(self):
        return f"<Category {self.name}>"
