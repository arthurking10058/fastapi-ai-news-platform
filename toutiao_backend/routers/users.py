from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.crud import users
from toutiao_backend.models.users import User
from toutiao_backend.schemas.users import (
    UserAuthResponse,
    UserChangePasswordRequest,
    UserInfoResponse,
    UserRequest,
    UserUpdateRequest,
)
from toutiao_backend.utils.auth import get_current_user
from toutiao_backend.utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(
    user_data: UserRequest,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在",
        )

    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(user),
    )
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(
    user_data: UserRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(user),
    )
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(user),
    )


@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await users.update_user(db, user.username, user_data)
    return success_response(
        message="更新用户信息成功",
        data=UserInfoResponse.model_validate(updated_user),
    )


@router.put("/password")
async def update_password(
    password_data: UserChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    changed = await users.change_password(db, user, password_data)
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请稍后再试",
        )

    return success_response(message="修改密码成功")
