from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship, Mapped, mapped_column, backref
from sqlalchemy.sql import expression, func
from sqlalchemy.sql.sqltypes import TIMESTAMP


@as_declarative()
class Base:
    """Базовая модель."""

    id = Column(Integer, primary_key=True, unique=True)
    __name__: str


users_categories = Table(
    "users_categories",
    Base.metadata,
    Column("category_id", ForeignKey("categories.id"), primary_key=True, unique=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True, unique=True)
)


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String(32), unique=True, nullable=True)
    email = Column(String(48), unique=True, nullable=True)
    external_id = Column(Integer, unique=True, nullable=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    has_mailing = Column(Boolean, default=False)
    date_registration = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    external_signup_date = Column(TIMESTAMP, nullable=True)
    banned = Column(Boolean, server_default=expression.false(), nullable=False)

    categories: Mapped[list["Category"]] = relationship(
        secondary="users_categories", back_populates="users")

    def __repr__(self):
        return f"<User {self.telegram_id}>"


class Task(Base):
    """Модель задач."""

    __tablename__ = "tasks"
    title = Column(String)
    name_organization = Column(String)
    deadline = Column(Date)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="tasks")

    bonus = Column(Integer)
    location = Column(String)
    link = Column(String)
    description = Column(String)
    archive = Column(Boolean)
    created_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_date = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class Category(Base):
    """Модель категорий."""

    __tablename__ = "categories"
    name = Column(String(100))
    archive = Column(Boolean())

    users: Mapped[list["User"]] = relationship(
        secondary="users_categories", back_populates="categories"
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")

    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    children = relationship(
        "Category",
        uselist=True,
        backref=backref("parent", remote_side="Category.id"),
        lazy="subquery",
        join_depth=1,
    )

    def __repr__(self):
        return f"<Category {self.name}>"
