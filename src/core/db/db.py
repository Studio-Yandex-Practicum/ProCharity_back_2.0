from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.settings import settings

engine = create_async_engine(settings.database_url)


async def get_session(
    sessionmaker=async_sessionmaker(engine, expire_on_commit=False)
) -> Generator[AsyncSession, None, None]:
    async with sessionmaker() as session:
        yield session
