import asyncio


from src.core.db import get_session
from src.core.db.models import Category, User


async def main():
    session = get_session()

    user = User(
        telegram_id=1,
        username="username",
    )
    category = Category(
        name="test",
        archive=False,
        users=[user],
    )
    await session.add_all((user, category))
    await session.delete(category)
    await session.delete(user)

if __name__ == "__main__":
    asyncio.run(main())
