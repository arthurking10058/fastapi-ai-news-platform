import asyncio
import logging
from datetime import datetime

from sqlalchemy import func, select

from toutiao_backend.config.db_conf import AsyncSessionLocal, create_tables
from toutiao_backend.models.favorite import Favorite
from toutiao_backend.models.history import History
from toutiao_backend.models.news import Category, News
from toutiao_backend.models.users import User
from toutiao_backend.utils.security import get_hash_password

logger = logging.getLogger(__name__)


DEMO_CATEGORIES = [
    {"id": 1, "name": "头条", "sort_order": 1},
    {"id": 2, "name": "社会", "sort_order": 2},
    {"id": 3, "name": "科技", "sort_order": 3},
]

DEMO_NEWS = [
    {
        "id": 1,
        "title": "2024 年头条新闻示例一",
        "description": "演示用头条新闻一",
        "content": "这是用于演示的头条新闻正文一。",
        "image": "https://example.com/demo-1.jpg",
        "author": "演示作者",
        "category_id": 1,
        "views": 1280,
        "publish_time": datetime(2024, 1, 10, 9, 0, 0),
    },
    {
        "id": 2,
        "title": "2024 年头条新闻示例二",
        "description": "演示用头条新闻二",
        "content": "这是用于演示的头条新闻正文二。",
        "image": "https://example.com/demo-2.jpg",
        "author": "演示作者",
        "category_id": 1,
        "views": 960,
        "publish_time": datetime(2024, 2, 12, 10, 0, 0),
    },
    {
        "id": 3,
        "title": "2024 年头条新闻示例三",
        "description": "演示用头条新闻三",
        "content": "这是用于演示的头条新闻正文三。",
        "image": "https://example.com/demo-3.jpg",
        "author": "演示作者",
        "category_id": 1,
        "views": 820,
        "publish_time": datetime(2024, 3, 18, 11, 0, 0),
    },
    {
        "id": 4,
        "title": "社会新闻示例一",
        "description": "演示用社会新闻",
        "content": "这是用于演示的社会新闻正文。",
        "image": "https://example.com/demo-4.jpg",
        "author": "演示作者",
        "category_id": 2,
        "views": 420,
        "publish_time": datetime(2024, 4, 20, 8, 30, 0),
    },
    {
        "id": 5,
        "title": "科技新闻示例一",
        "description": "演示用科技新闻",
        "content": "这是用于演示的科技新闻正文。",
        "image": "https://example.com/demo-5.jpg",
        "author": "演示作者",
        "category_id": 3,
        "views": 560,
        "publish_time": datetime(2024, 5, 2, 9, 15, 0),
    },
    {
        "id": 6,
        "title": "科技新闻示例二",
        "description": "演示用科技新闻二",
        "content": "这是用于演示的科技新闻正文二。",
        "image": "https://example.com/demo-6.jpg",
        "author": "演示作者",
        "category_id": 3,
        "views": 610,
        "publish_time": datetime(2024, 5, 20, 14, 0, 0),
    },
]


async def wait_for_database() -> None:
    for _ in range(60):
        try:
            await create_tables()
            async with AsyncSessionLocal() as session:
                await session.execute(select(1))
            return
        except Exception as exc:  # pragma: no cover
            logger.info("Database not ready yet: %s", exc)
            await asyncio.sleep(2)
    raise RuntimeError("Database is not ready")


async def ensure_categories(session) -> None:
    count_result = await session.execute(select(func.count(Category.id)))
    if count_result.scalar_one() > 0:
        return

    session.add_all(Category(**item) for item in DEMO_CATEGORIES)
    await session.commit()


async def ensure_news(session) -> None:
    count_result = await session.execute(select(func.count(News.id)))
    if count_result.scalar_one() > 0:
        return

    session.add_all(News(**item) for item in DEMO_NEWS)
    await session.commit()


async def ensure_demo_user(session) -> User | None:
    result = await session.execute(select(User).where(User.username == "admin"))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        username="admin",
        password=get_hash_password("123456"),
        nickname="演示管理员",
        bio="用于 Docker 演示的示例账号",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def ensure_demo_relations(session, user: User | None) -> None:
    if not user:
        return

    favorite_count = await session.execute(
        select(func.count(Favorite.id)).where(Favorite.user_id == user.id)
    )
    if favorite_count.scalar_one() == 0:
        session.add(Favorite(user_id=user.id, news_id=1))

    history_count = await session.execute(
        select(func.count(History.id)).where(History.user_id == user.id)
    )
    if history_count.scalar_one() == 0:
        session.add(History(user_id=user.id, news_id=1))

    await session.commit()


async def main() -> None:
    await wait_for_database()
    async with AsyncSessionLocal() as session:
        await ensure_categories(session)
        await ensure_news(session)
        user = await ensure_demo_user(session)
        await ensure_demo_relations(session, user)
    logger.info("Demo data seeded successfully")


if __name__ == "__main__":
    asyncio.run(main())
