from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from toutiao_backend.schemas.base import ORMBaseModel


class UserRequest(BaseModel):
    username: str
    password: str

class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True #允许从ORM对象属性中取值
    )

#data数据类型
class UserAuthResponse(ORMBaseModel):
    token: str
    user_info: UserInfoResponse = Field(...,alias="userInfo")
    model_config = ConfigDict(
        populate_by_name = True,
        from_attributes=True
    )


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(...,alias="oldPassword",description="旧密码")
    new_password: str = Field(...,alias="newPassword", min_length=6,description="新密码")
