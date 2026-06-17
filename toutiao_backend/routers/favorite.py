from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.crud import favorite
from toutiao_backend.models.users import User
from toutiao_backend.schemas.favorite import (
    FavoriteAddRequest,
    FavoriteCheckResponse,
    FavoriteListResponse,
    FavoriteNewsItemResponse,
)
from toutiao_backend.utils.auth import get_current_user
from toutiao_backend.utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)
    return success_response(
        message="检查收藏状态成功",
        data=FavoriteCheckResponse(isFavorite=is_favorited),
    )


@router.post("/add")
async def add_favorite(
    data: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功", data=result)


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await favorite.remove_news_favorite(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return success_response(message="删除收藏成功")


@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [
        FavoriteNewsItemResponse.model_validate(
            {
                **news_item.__dict__,
                "favorite_id": favorite_id,
                "favorite_time": favorite_time,
            }
        )
        for news_item, favorite_time, favorite_id in rows
    ]
    has_more = total > page * page_size

    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)


@router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await favorite.remove_all_favorites(db, user.id)
    return success_response(message=f"清空成功，共删除 {count} 条记录")
