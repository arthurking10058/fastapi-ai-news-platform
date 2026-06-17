from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from toutiao_backend.models.ai_chat import AIChat
from toutiao_backend.models.base import Base
from toutiao_backend.models.favorite import Favorite
from toutiao_backend.models.history import History
from toutiao_backend.models.news import Category, News
from toutiao_backend.models.related_news import RelatedNews
from toutiao_backend.models.users import User, UserToken
from toutiao_backend.config.settings import get_settings

settings = get_settings()

async_engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_existing_table_columns(conn)


async def ensure_existing_table_columns(conn) -> None:
    await ensure_column(
        conn,
        "history",
        "created_at",
        "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
    )
    await ensure_column(
        conn,
        "history",
        "updated_at",
        "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    )


async def ensure_column(conn, table_name: str, column_name: str, definition: str) -> None:
    result = await conn.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )

    if result.scalar_one() == 0:
        await conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
