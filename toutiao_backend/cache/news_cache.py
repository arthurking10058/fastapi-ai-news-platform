from typing import Any, Optional

from toutiao_backend.config.cache_conf import get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
NEWS_DETAIL_PREFIX = "news:detail:"
RELATED_NEWS_PREFIX = "news:related:"


async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


async def set_cache_categories(data: list[dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


async def set_cache_news_list(
    category_id: Optional[int],
    page: int,
    size: int,
    news_list: list[dict[str, Any]],
    expire: int = 1800,
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)


async def get_cache_news_list(category_id: Optional[int], page: int, size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)


async def get_cached_news_detail(news_id: int) -> Optional[dict[str, Any]]:
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await get_json_cache(key)


async def cache_news_detail(news_id: int, news_data: dict[str, Any], expire: int = 300) -> bool:
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await set_cache(key, news_data, expire)


async def cache_related_news(
    news_id: int,
    category_id: int,
    related_list: list[dict[str, Any]],
    expire: int = 1800,
) -> bool:
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await set_cache(key, related_list, expire)


async def get_cached_related_news(
    news_id: int,
    category_id: int,
) -> Optional[list[dict[str, Any]]]:
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await get_json_cache(key)
