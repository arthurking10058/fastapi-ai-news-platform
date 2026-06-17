from typing import Any, cast

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.cache.news_cache import (
    cache_news_detail,
    cache_related_news,
    get_cache_news_list,
    get_cached_categories,
    get_cached_news_detail,
    get_cached_related_news,
    set_cache_categories,
    set_cache_news_list,
)
from toutiao_backend.models.news import Category, News
from toutiao_backend.schemas.base import NewsItemBase
from toutiao_backend.schemas.news import NewsDetailResponse, RelatedNewsResponse


async def get_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = list(result.scalars().all())

    if categories:
        categories_data = jsonable_encoder(categories)
        await set_cache_categories(categories_data)
        return categories_data

    return []


async def get_news_list(
    db: AsyncSession,
    category_id: int,
    skip: int = 0,
    limit: int = 10,
) -> list[News]:
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)
    if cached_list:
        return [News(**item) for item in cached_list]

    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    news_list = list(result.scalars().all())

    if news_list:
        news_data = [
            NewsItemBase.model_validate(item).model_dump(
                mode="json",
                by_alias=False,
            )
            for item in news_list
        ]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


async def get_news_count(db: AsyncSession, category_id: int) -> int:
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return int(result.scalar_one())


async def get_news_detail(db: AsyncSession, news_id: int) -> News | None:
    cached_news = await get_cached_news_detail(news_id)
    if cached_news:
        return News(**cached_news)

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()

    if news:
        news_dict = NewsDetailResponse.model_validate(news).model_dump(
            by_alias=False,
            mode="json",
            exclude={"related_news"},
        )
        await cache_news_detail(news_id, news_dict)

    return news


async def increase_news_views(db: AsyncSession, news_id: int) -> bool:
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    cursor_result = cast(CursorResult[Any], result)
    return (cursor_result.rowcount or 0) > 0


async def get_related_news(
    db: AsyncSession,
    news_id: int,
    category_id: int,
    limit: int = 5,
) -> list[dict[str, Any]]:
    cached_related = await get_cached_related_news(news_id, category_id)
    if cached_related:
        return cached_related

    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.views.desc(), News.publish_time.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    related_news = list(result.scalars().all())

    if related_news:
        related_data = [
            RelatedNewsResponse.model_validate(item).model_dump(
                by_alias=False,
                mode="json",
            )
            for item in related_news
        ]
        await cache_related_news(news_id, category_id, related_data)
        return related_data

    return []
