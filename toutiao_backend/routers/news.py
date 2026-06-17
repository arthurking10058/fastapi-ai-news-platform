from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.crud import news
from toutiao_backend.schemas.news import (
    NewsDetailResponse,
    NewsItemResponse,
    RelatedNewsResponse,
)
from toutiao_backend.utils.response import success_response

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    categories = await news.get_categories(db, skip, limit)
    return success_response(message="获取新闻分类成功", data=categories)


@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)

    return success_response(
        message="获取新闻列表成功",
        data={
            "list": [NewsItemResponse.model_validate(item) for item in news_list],
            "total": None,
            "hasMore": len(news_list) == page_size,
        },
    )


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),
    db: AsyncSession = Depends(get_db),
):
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    await news.increase_news_views(db, news_detail.id)
    related_news = await news.get_related_news(
        db,
        news_detail.id,
        news_detail.category_id,
    )

    data = NewsDetailResponse.model_validate(news_detail).model_dump(by_alias=True)
    data["relatedNews"] = [
        RelatedNewsResponse.model_validate(item).model_dump(by_alias=True)
        for item in related_news
    ]
    return success_response(message="获取新闻详情成功", data=data)
