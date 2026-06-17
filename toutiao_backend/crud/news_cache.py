"""Legacy learning file.

The active news business logic lives in ``toutiao_backend.crud.news``.
This module is kept only as a compatibility alias during the learning phase.
"""

from toutiao_backend.crud.news import (
    get_categories,
    get_news_count,
    get_news_detail,
    get_news_list,
    get_related_news,
    increase_news_views,
)

__all__ = [
    "get_categories",
    "get_news_count",
    "get_news_detail",
    "get_news_list",
    "get_related_news",
    "increase_news_views",
]
