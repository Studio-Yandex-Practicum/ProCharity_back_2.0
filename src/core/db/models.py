from sqlalchemy import (
    BigInteger, Column, Date, ForeignKey, Integer, String, Table)
from sqlalchemy.orm import (
    relationship, Mapped, mapped_column, backref, DeclarativeBase)
from sqlalchemy.sql import expression, func
from datetime import date
from abc import ABC

class Base(DeclarativeBase):
    """Основа для базового класса."""

    id: Mapped[int] = mapped_column(primary_key=True)
    __name__: Mapped[str]


users_categories = Table(
    "users_categories",
    Base.metadata,
    Column(
        "category_id", ForeignKey("categories.id"),
        primary_key=True, unique=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True, unique=True),
)


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(48), unique=True, nullable=True)
    external_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    has_mailing: Mapped[bool] = mapped_column(default=False)
    date_registration: Mapped[date] = mapped_column(
        server_default=func.current_timestamp(), nullable=False)
    external_signup_date: Mapped[date] = mapped_column(nullable=True)
    banned: Mapped[bool] = mapped_column(
        server_default=expression.false(), nullable=False)

    categories: Mapped[list["Category"]] = relationship(
        secondary="users_categories", back_populates="users")

    def __repr__(self):
        return f"<User {self.telegram_id}>"


class Content(Base, ABC):
    __abstract__ = True
    is_archive: Mapped[bool]


class Task(Content):
    """Модель задач."""

    __tablename__ = "tasks"
    title = Mapped[str]
    name_organization = Mapped[str]
    deadline = Mapped[Date]

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="tasks")

    bonus = Mapped[int]
    location = Mapped[str]
    link = Mapped[str]
    description = Mapped[str]
    is_archive = Mapped[bool]
    created_date: Mapped[date] = mapped_column(
        server_default=func.current_timestamp(), nullable=False
    )
    updated_date: Mapped[date] = mapped_column(
        server_default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class Category(Content):
    """Модель категорий."""

    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(100))
    is_archive: Mapped[bool]

    users: Mapped[list["User"]] = relationship(
        secondary="users_categories", back_populates="categories"
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")

    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True)
    children = relationship(
        "Category", backref=backref("parent", remote_side="Category.id"))

    def __repr__(self):
        return f"<Category {self.name}>"
