from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    """Базовая модель."""

    id = Column(Integer, primary_key=True)
    __name__: str


class Category1(Base):
    __tablename__='ctaegory'
    name = Column(Integer, nullable=False)
