from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from toutiao_backend.schemas.base import NewsItemBase


class CategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int = Field(alias="sortOrder")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class NewsItemResponse(NewsItemBase):
    publish_time: Optional[datetime] = Field(None, alias="publishTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class RelatedNewsResponse(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    views: int

    model_config = ConfigDict(from_attributes=True)


class NewsDetailResponse(NewsItemBase):
    content: str
    related_news: list[RelatedNewsResponse] = Field(
        default_factory=list,
        alias="relatedNews",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
