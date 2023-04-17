import asyncio
import contextlib

from src.core.db import get_session
from src.core.db.models import Category, User, Task


async def main():
    get_async_session_context = contextlib.asynccontextmanager(get_session)
    async with get_async_session_context() as session:

        user = User(
            telegram_id=45,
            username="username45",
        )
        task = Task(
            title="Важный таск"
        )
        category = Category(
            name="test",
            archive=False,
            users=[user],
            tasks=[task]
        )

        session.add(user)
        session.add(task)
        session.add(category)

        await session.commit()

        await session.delete(category)
        await session.delete(user)
        await session.delete(task)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
