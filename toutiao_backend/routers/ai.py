import asyncio
import json
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.config.ai_conf import get_ai_chat_settings
from toutiao_backend.config.db_conf import get_db
from toutiao_backend.models.news import News
from toutiao_backend.schemas.ai import AIChatRequest, AIHotNewsItem
from toutiao_backend.utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["ai"])

HOT_NEWS_LIMIT = 5


@router.post("/chat")
async def chat_with_news_context(
    payload: AIChatRequest,
    db: AsyncSession = Depends(get_db),
):
    settings = get_ai_chat_settings()

    if is_2024_headline_hot_news_question(payload.question):
        hot_news = await get_2024_headline_hot_news(db)
        news_items = [serialize_hot_news(item) for item in hot_news]
        answer, source = await answer_hot_news_question(payload, news_items, settings)
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


def is_2024_headline_hot_news_question(question: str) -> bool:
    text = question.lower().replace(" ", "")
    has_2024 = any(keyword in text for keyword in ("2024", "24年", "二零二四", "二〇二四"))
    has_headline = any(keyword in text for keyword in ("头条", "category_id=1", "分类1"))
    has_hot_rank = any(
        keyword in text
        for keyword in (
            "浏览最多",
            "浏览量最高",
            "阅读最多",
            "阅读量最高",
            "最多",
            "最高",
            "排行",
            "排名",
            "热门",
        )
    )
    return has_2024 and has_headline and has_hot_rank


async def answer_hot_news_question(
    payload: AIChatRequest,
    news_items: list[AIHotNewsItem],
    settings,
) -> tuple[str, str]:
    fallback_answer = build_hot_news_answer(news_items)
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
            f"我是这个新闻项目里的 AI 助手。当前后端没有配置 AI_API_KEY，所以只能回答项目内置查询；后端默认模型配置是 {settings.model}。",
            "fallback",
        )

    try:
        answer = await ask_model(payload, settings, build_general_system_messages(settings.model))
        return answer, "ai"
    except Exception as exc:
        return f"模型暂时不可用，请稍后再试。原因：{exc}", "fallback"


async def get_2024_headline_hot_news(db: AsyncSession) -> list[News]:
    stmt = (
        select(News)
        .where(
            News.category_id == 1,
            News.publish_time >= datetime(2024, 1, 1),
            News.publish_time < datetime(2025, 1, 1),
        )
        .order_by(desc(News.views), desc(News.publish_time))
        .limit(HOT_NEWS_LIMIT)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def serialize_hot_news(item: News) -> AIHotNewsItem:
    return AIHotNewsItem(
        id=item.id,
        title=item.title,
        description=item.description,
        author=item.author,
        views=item.views,
        publishTime=item.publish_time.strftime("%Y-%m-%d %H:%M:%S"),
    )


def build_hot_news_answer(news_items: list[AIHotNewsItem]) -> str:
    if not news_items:
        return "我查询了数据库：2024 年、头条分类下暂时没有找到新闻记录。"

    lines = ["根据当前数据库查询，2024 年浏览量最高的头条新闻如下："]
    for index, item in enumerate(news_items, start=1):
        lines.append(
            f"{index}. {item.title}，浏览量 {item.views}，发布时间 {item.publish_time}"
        )
        if item.description:
            lines.append(f"   简介：{item.description}")
    return "\n".join(lines)


def build_news_system_messages(news_items: list[AIHotNewsItem]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是新闻项目里的 AI 助手。回答涉及新闻排行、浏览量、2024 年头条新闻时，"
                "必须只依赖后端提供的数据库查询结果，不能编造不存在的数据。"
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
