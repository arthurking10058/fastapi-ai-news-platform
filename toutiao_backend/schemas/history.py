from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from toutiao_backend.schemas.news import NewsItemResponse


class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

    model_config = ConfigDict(populate_by_name=True)


class HistoryNewsItemResponse(NewsItemResponse):
    history_id: int = Field(alias="historyId")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: Optional[int] = None
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(populate_by_name=True)
