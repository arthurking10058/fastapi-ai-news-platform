import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def load_local_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class AppSettings:
    database_url: str
    redis_host: str
    redis_port: int
    redis_db: int
    cache_retry_interval: int
    ai_api_endpoint: str
    ai_api_key: str
    ai_model: str
    ai_timeout: float
    debug: bool
    cors_origins: list[str]


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return ["*"]

    origins = [item.strip() for item in value.split(",") if item.strip()]
    return origins or ["*"]


@lru_cache
def get_settings() -> AppSettings:
    load_local_env()
    return AppSettings(
        database_url=os.getenv(
            "DATABASE_URL",
            "mysql+aiomysql://root:123456@127.0.0.1:3306/news_app?charset=utf8mb4",
        ),
        redis_host=os.getenv("REDIS_HOST", "127.0.0.1"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_db=int(os.getenv("REDIS_DB", "0")),
        cache_retry_interval=int(os.getenv("CACHE_RETRY_INTERVAL", "30")),
        ai_api_endpoint=os.getenv(
            "AI_API_ENDPOINT",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        ),
        ai_api_key=os.getenv("AI_API_KEY", ""),
        ai_model=os.getenv("AI_MODEL", "qwen-max"),
        ai_timeout=float(os.getenv("AI_TIMEOUT", "30")),
        debug=_parse_bool(os.getenv("DEBUG"), default=False),
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
    )
