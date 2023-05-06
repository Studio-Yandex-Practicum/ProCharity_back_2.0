from typing import Generator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from contextlib import asynccontextmanager
from src.settings import settings

engine = create_async_engine(settings.database_url)

@asynccontextmanager
async def get_session() -> Generator[AsyncSession, None, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
