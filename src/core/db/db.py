from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.settings import settings

engine = create_async_engine(settings.database_url)

AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with AsyncSession() as session:
        yield session
