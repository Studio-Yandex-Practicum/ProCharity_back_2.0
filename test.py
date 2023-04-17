import asyncio
import contextlib

from src.core.db import get_session
from src.core.db.models import Category, User


async def main():
    get_async_session_context = contextlib.asynccontextmanager(get_session)
    async with get_async_session_context() as session:
        user = User(
            # id=2,
            telegram_id=1,
            username="username1",
        )
        category = Category(
            name="test",
            archive=False,
            users=[user],
        )
        session.add(user)
        session.add(category)
        await session.commit()
        # await session.add_all((user, category))
        await session.delete(category)
        await session.delete(user)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
