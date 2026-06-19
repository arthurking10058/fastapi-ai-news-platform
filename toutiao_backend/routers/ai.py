import asyncio
import json
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.config.ai_conf import get_ai_chat_settings
from toutiao_backend.config.db_conf import get_db
from toutiao_backend.models.news import Category, News
from toutiao_backend.schemas.ai import AIChatRequest, AIHotNewsItem
from toutiao_backend.utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["ai"])

HOT_NEWS_LIMIT = 5
GENERAL_NEWS_LIMIT = 5
CATEGORY_NAME_GROUPS = {
    "headline": ("头条",),
    "society": ("社会",),
    "technology": ("科技",),
    "sports": ("体育",),
    "finance": ("财经",),
}


@router.post("/chat")
async def chat_with_news_context(
    payload: AIChatRequest,
    db: AsyncSession = Depends(get_db),
):
    settings = get_ai_chat_settings()

    if is_2024_headline_hot_news_question(payload.question):
        hot_news = await get_2024_headline_hot_news(db)
        news_items = limit_news_items(
            [serialize_hot_news(item) for item in hot_news],
            payload.question,
        )
        answer, source = await answer_news_question(
            payload,
            news_items,
            settings,
            build_hot_news_answer(news_items),
        )
    elif should_query_database_first(payload.question):
        matched_news = await get_relevant_news_from_db(db, payload.question)
        news_items = limit_news_items(
            [serialize_hot_news(item) for item in matched_news],
            payload.question,
        )
        answer, source = await answer_news_question(
            payload,
            news_items,
            settings,
            build_news_lookup_answer(payload.question, news_items),
        )
    else:
        news_items = []
        answer, source = await answer_general_question(payload, settings)

    return success_response(
        message="AI问答成功",
        data={
            "answer": answer,
            "news": [item.model_dump(by_alias=True) for item in news_items],
            "source": source,
        },
    )


def normalize_question_text(question: str) -> str:
    return question.lower().replace(" ", "")


def is_2024_headline_hot_news_question(question: str) -> bool:
    text = normalize_question_text(question)
    has_2024 = any(keyword in text for keyword in ("2024", "24年", "二零二四", "二〇二四"))
    has_headline = any(
        keyword in text
        for keyword in ("头条", "headline", "首页", "category_id=1", "分类1")
    )
    has_hot_rank = any(
        keyword in text
        for keyword in (
            "浏览最多",
            "浏览量最高",
            "阅读最多",
            "阅读量最高",
            "最火",
            "最热门",
            "最热",
            "最多",
            "最高",
            "排行",
            "排名",
            "热门",
        )
    )
    return has_2024 and has_headline and has_hot_rank


def should_query_database_first(question: str) -> bool:
    text = normalize_question_text(question)
    news_keywords = (
        "新闻",
        "头条",
        "热点",
        "热搜",
        "排行",
        "排名",
        "最火",
        "最热",
        "热门",
        "科技",
        "体育",
        "社会",
        "运动",
        "明星",
        "娱乐",
        "游戏",
        "奥运",
        "ai",
        "人工智能",
        "苹果",
        "openai",
        "财经",
        "财政",
        "财税",
        "金融",
        "股市",
        "证券",
        "基金",
        "经济",
    )
    return any(keyword in text for keyword in news_keywords)


def get_requested_news_limit(question: str) -> int:
    text = normalize_question_text(question)
    if any(keyword in text for keyword in ("一条", "1条", "一篇", "1篇", "一个")):
        return 1
    if any(keyword in text for keyword in ("两条", "2条", "两篇", "2篇", "两个")):
        return 2
    if any(keyword in text for keyword in ("三条", "3条", "三篇", "3篇", "三个")):
        return 3
    return GENERAL_NEWS_LIMIT


def limit_news_items(news_items: list[AIHotNewsItem], question: str) -> list[AIHotNewsItem]:
    return news_items[: get_requested_news_limit(question)]


async def answer_news_question(
    payload: AIChatRequest,
    news_items: list[AIHotNewsItem],
    settings,
    fallback_answer: str,
) -> tuple[str, str]:
    if not news_items:
        return fallback_answer, "database"

    if not settings.api_key:
        return fallback_answer, "database"

    try:
        answer = await ask_model(payload, settings, build_news_system_messages(news_items))
        return answer, "ai"
    except Exception as exc:
        return (
            f"{fallback_answer}\n\n模型总结暂时不可用，已先返回数据库查询结果。原因：{exc}",
            "fallback",
        )


async def answer_general_question(payload: AIChatRequest, settings) -> tuple[str, str]:
    if not settings.api_key:
        return (
            (
                "我是这个新闻项目里的 AI 助手。当前后端没有配置 AI_API_KEY，"
                f"所以只能回答项目内置查询；后端默认模型配置是 {settings.model}。"
            ),
            "fallback",
        )

    try:
        answer = await ask_model(payload, settings, build_general_system_messages(settings.model))
        return answer, "ai"
    except Exception as exc:
        return f"模型暂时不可用，请稍后再试。原因：{exc}", "fallback"


async def get_2024_headline_hot_news(db: AsyncSession) -> list[News]:
    headline_category_ids = await get_category_ids_by_group(db, "headline")
    if not headline_category_ids:
        return []

    stmt = (
        select(News)
        .where(
            News.category_id.in_(headline_category_ids),
            News.publish_time >= datetime(2024, 1, 1),
            News.publish_time < datetime(2025, 1, 1),
        )
        .order_by(desc(News.views), desc(News.publish_time))
        .limit(HOT_NEWS_LIMIT)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_relevant_news_from_db(db: AsyncSession, question: str) -> list[News]:
    text = normalize_question_text(question)
    stmt = select(News)
    matched_category_group = None
    category_specific_keywords: set[str] = set()

    if any(keyword in text for keyword in ("2024", "24年", "二零二四", "二〇二四")):
        stmt = stmt.where(
            News.publish_time >= datetime(2024, 1, 1),
            News.publish_time < datetime(2025, 1, 1),
        )

    if any(keyword in text for keyword in ("头条", "headline", "首页")):
        matched_category_group = "headline"
        category_specific_keywords = {"头条", "headline", "首页"}
    elif "社会" in text:
        matched_category_group = "society"
        category_specific_keywords = {"社会"}
    elif any(keyword in text for keyword in ("科技", "ai", "人工智能", "游戏", "苹果", "openai")):
        matched_category_group = "technology"
        category_specific_keywords = {"科技", "ai", "人工智能", "游戏", "苹果", "openai"}
    elif any(keyword in text for keyword in ("体育", "运动", "奥运", "足球", "网球", "游泳")):
        matched_category_group = "sports"
        category_specific_keywords = {"体育", "运动", "奥运", "足球", "网球", "游泳"}
    elif any(keyword in text for keyword in ("财经", "财政", "财税", "金融", "股市", "证券", "基金", "经济")):
        matched_category_group = "finance"
        category_specific_keywords = {"财经", "财政", "财税", "金融", "股市", "证券", "基金", "经济"}

    if matched_category_group is not None:
        matched_category_ids = await get_category_ids_by_group(db, matched_category_group)
        if not matched_category_ids:
            return []
        stmt = stmt.where(News.category_id.in_(matched_category_ids))

    keyword_conditions = []
    for keyword in (
        "明星",
        "娱乐",
        "运动",
        "体育",
        "科技",
        "财经",
        "财政",
        "财税",
        "金融",
        "股市",
        "证券",
        "基金",
        "经济",
        "游戏",
        "ai",
        "人工智能",
        "奥运",
        "苹果",
        "openai",
    ):
        if keyword in text and keyword not in category_specific_keywords:
            keyword_conditions.extend(
                [
                    News.title.contains(keyword),
                    News.description.contains(keyword),
                    News.content.contains(keyword),
                ]
            )

    if keyword_conditions:
        stmt = stmt.where(or_(*keyword_conditions))
    elif matched_category_group is None and not any(
        keyword in text for keyword in ("2024", "24年", "二零二四", "二〇二四")
    ):
        return []

    if any(keyword in text for keyword in ("最火", "最热", "最热门", "热门", "排行", "排名", "最多", "最高")):
        stmt = stmt.order_by(desc(News.views), desc(News.publish_time))
    else:
        stmt = stmt.order_by(desc(News.publish_time), desc(News.views))

    stmt = stmt.limit(GENERAL_NEWS_LIMIT)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category_ids_by_group(db: AsyncSession, group: str) -> list[int]:
    names = CATEGORY_NAME_GROUPS.get(group, ())
    if not names:
        return []

    stmt = select(Category.id).where(Category.name.in_(names))
    result = await db.execute(stmt)
    return list(result.scalars().all())


def serialize_hot_news(item: News) -> AIHotNewsItem:
    return AIHotNewsItem(
        id=item.id,
        title=item.title,
        description=item.description,
        author=item.author,
        image=item.image,
        views=item.views,
        publishTime=item.publish_time.strftime("%Y-%m-%d %H:%M:%S"),
    )


def build_hot_news_answer(news_items: list[AIHotNewsItem]) -> str:
    if not news_items:
        return "我查询了数据库：2024 年、头条分类下暂时没有找到新闻记录。"

    if len(news_items) == 1:
        item = news_items[0]
        lines = [
            "根据当前数据库查询，最符合条件的一条头条新闻如下：",
            f"1. {item.title}，浏览量 {item.views}，发布时间 {item.publish_time}",
        ]
        if item.description:
            lines.append(f"   简介：{item.description}")
        return "\n".join(lines)

    lines = ["根据当前数据库查询，2024 年浏览量最高的头条新闻如下："]
    for index, item in enumerate(news_items, start=1):
        lines.append(
            f"{index}. {item.title}，浏览量 {item.views}，发布时间 {item.publish_time}"
        )
        if item.description:
            lines.append(f"   简介：{item.description}")
    return "\n".join(lines)


def build_news_lookup_answer(question: str, news_items: list[AIHotNewsItem]) -> str:
    if not news_items:
        query_scope = describe_query_scope(question)
        if query_scope:
            return f"我查询了当前数据库，但当前数据库暂无{query_scope}相关新闻记录。"
        return f"我查询了当前数据库，但没有找到与“{question}”相关的新闻记录。"

    if len(news_items) == 1:
        item = news_items[0]
        lines = [f"根据当前数据库，和“{question}”最相关的一条新闻如下："]
        lines.append(
            f"1. {item.title}，浏览量 {item.views}，发布时间 {item.publish_time}"
        )
        if item.description:
            lines.append(f"   简介：{item.description}")
        return "\n".join(lines)

    lines = [f"根据当前数据库，和“{question}”最相关的新闻如下："]
    for index, item in enumerate(news_items, start=1):
        lines.append(
            f"{index}. {item.title}，浏览量 {item.views}，发布时间 {item.publish_time}"
        )
        if item.description:
            lines.append(f"   简介：{item.description}")
    return "\n".join(lines)


def describe_query_scope(question: str) -> str:
    text = normalize_question_text(question)
    year = ""
    if any(keyword in text for keyword in ("2024", "24年", "二零二四", "二〇二四")):
        year = "2024年"

    category = ""
    if any(keyword in text for keyword in ("头条", "headline", "首页")):
        category = "头条"
    elif "社会" in text:
        category = "社会"
    elif any(keyword in text for keyword in ("科技", "ai", "人工智能", "游戏", "苹果", "openai")):
        category = "科技"
    elif any(keyword in text for keyword in ("体育", "运动", "奥运", "足球", "网球", "游泳")):
        category = "体育"
    elif any(keyword in text for keyword in ("财经", "财政", "财税", "金融", "股市", "证券", "基金", "经济")):
        category = "财经"

    return f"{year}{category}" if year or category else ""


def build_news_system_messages(news_items: list[AIHotNewsItem]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是新闻项目里的 AI 助手。只要后端已经提供了数据库查询结果，"
                "你就必须优先依据这些结果回答，不能编造不存在的新闻。"
            ),
        },
        {
            "role": "system",
            "content": "数据库查询结果：" + json.dumps(
                [item.model_dump(by_alias=True) for item in news_items],
                ensure_ascii=False,
            ),
        },
    ]


def build_general_system_messages(model: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是新闻项目里的 AI 助手。普通聊天问题请直接回答；"
                f"如果用户问你是什么模型，可以说明后端当前配置的模型是 {model}。"
            ),
        }
    ]


async def ask_model(
    payload: AIChatRequest,
    settings,
    system_messages: list[dict[str, str]],
) -> str:
    messages = [*system_messages]
    for message in payload.messages[-8:]:
        if message.role != "system":
            messages.append({"role": message.role, "content": message.content})

    if not messages or messages[-1]["role"] != "user":
        messages.append({"role": "user", "content": payload.question})

    request_body = {
        "model": settings.model,
        "messages": messages,
        "stream": False,
    }
    return await asyncio.to_thread(call_openai_compatible_api, settings, request_body)


def call_openai_compatible_api(settings, request_body: dict) -> str:
    request = Request(
        settings.api_endpoint,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"AI 接口返回 {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"AI 接口连接失败: {exc.reason}") from exc

    data = json.loads(raw)
    content = data.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        content = data.get("output", {}).get("text")
    if not content:
        raise RuntimeError("AI 接口没有返回可用内容")
    return content
