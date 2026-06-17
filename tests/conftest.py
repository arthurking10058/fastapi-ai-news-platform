from collections.abc import AsyncIterator
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.main import app
from toutiao_backend.models.base import Base
from toutiao_backend.models.news import Category, News


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_app.db"

test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncIterator[AsyncSession]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def reset_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        categories = [
            Category(id=1, name="头条", sort_order=1),
            Category(id=2, name="科技", sort_order=2),
        ]
        session.add_all(categories)

        news_items = [
            News(
                id=1,
                title="头条新闻一",
                description="测试新闻一",
                content="测试内容一",
                image="https://example.com/1.jpg",
                author="测试作者",
                category_id=1,
                views=120,
                publish_time=datetime(2024, 1, 10, 8, 0, 0),
            ),
            News(
                id=2,
                title="头条新闻二",
                description="测试新闻二",
                content="测试内容二",
                image="https://example.com/2.jpg",
                author="测试作者",
                category_id=1,
                views=80,
                publish_time=datetime(2024, 2, 10, 8, 0, 0),
            ),
            News(
                id=3,
                title="科技新闻一",
                description="测试科技新闻",
                content="测试科技内容",
                image="https://example.com/3.jpg",
                author="科技作者",
                category_id=2,
                views=60,
                publish_time=datetime(2024, 3, 10, 8, 0, 0),
            ),
        ]
        session.add_all(news_items)
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture
async def auth_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/user/register",
        json={"username": "tester", "password": "123456"},
    )
    return response.json()["data"]["token"]
