from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.models.history import History
from toutiao_backend.models.news import News


async def add_history(db: AsyncSession, user_id: int, news_id: int) -> History:
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history

    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def get_history_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
):
    offset = (page - 1) * page_size
    query = (
        select(News, History.view_time.label("view_time"), History.id.label("history_id"))
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset)
        .limit(page_size + 1)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows[:page_size], len(rows) > page_size


async def delete_history(db: AsyncSession, user_id: int, history_id: int) -> bool:
    query = delete(History).where(History.user_id == user_id, History.id == history_id)
    result = await db.execute(query)
    await db.commit()
    return (result.rowcount or 0) > 0


async def clear_history(db: AsyncSession, user_id: int) -> int:
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0
