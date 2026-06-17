from dataclasses import dataclass
from functools import lru_cache

from toutiao_backend.config.settings import get_settings


@dataclass(frozen=True)
class AIChatSettings:
    api_endpoint: str
    api_key: str
    model: str
    timeout: float = 30.0


@lru_cache
def get_ai_chat_settings() -> AIChatSettings:
    settings = get_settings()
    return AIChatSettings(
        api_endpoint=settings.ai_api_endpoint,
        api_key=settings.ai_api_key,
        model=settings.ai_model,
        timeout=settings.ai_timeout,
    )


def ensure_ai_chat_settings() -> AIChatSettings:
    settings = get_ai_chat_settings()
    if not settings.api_key:
        raise ValueError(
            "未检测到 AI_API_KEY。请先在终端设置环境变量后再启动项目。"
        )
    return settings
