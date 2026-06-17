from typing import Literal

from pydantic import BaseModel, Field


class AIChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AIChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    messages: list[AIChatMessage] = Field(default_factory=list)


class AIHotNewsItem(BaseModel):
    id: int
    title: str
    description: str | None = None
    author: str | None = None
    views: int
    publish_time: str = Field(alias="publishTime")

    model_config = {
        "populate_by_name": True,
    }
