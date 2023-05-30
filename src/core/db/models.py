from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, backref, mapped_column, relationship
from sqlalchemy.sql import expression, func


class Base(DeclarativeBase):
    """Основа для базового класса."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[date] = mapped_column(
        server_default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp(),
    )
    __name__: Mapped[str]


class ContentBase(AbstractConcreteBase, Base):
    """Базовый класс для контента (категорий и задач)."""

    is_archived: Mapped[bool] = mapped_column(server_default=expression.false(), nullable=False)


class UsersCategories(Base):
    """Модель отношений пользователь-категория."""

    __tablename__ = "users_categories"

    id = None
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

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
    banned: Mapped[bool] = mapped_column(server_default=expression.false(), nullable=False)

    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary="users_categories", back_populates="users"
    )

    def __repr__(self):
        return f"<User {self.telegram_id}>"


class Task(ContentBase):
    """Модель задач."""

    __tablename__ = "tasks"
    title: Mapped[str] = mapped_column()
    name_organization: Mapped[str] = mapped_column(nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="tasks")

    bonus: Mapped[int]
    location: Mapped[str] = mapped_column()
    link: Mapped[str]
    description: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"<Task {self.title}>"


class Category(ContentBase):
    """Модель категорий."""

    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(100))

    users: Mapped[list["User"]] = relationship("User", secondary="users_categories", back_populates="categories")

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")

    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    children = relationship("Category", backref=backref("parent", remote_side="Category.id"))

    def __repr__(self):
        return f"<Category {self.name}>"
