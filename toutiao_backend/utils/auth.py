from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.crud import users
from toutiao_backend.models.users import User

UNAUTHORIZED_MESSAGE = "未登录或登录状态已失效"
INVALID_TOKEN_MESSAGE = "无效的令牌或令牌已过期"


async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_MESSAGE,
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_MESSAGE,
        )

    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_TOKEN_MESSAGE,
        )

    return user
