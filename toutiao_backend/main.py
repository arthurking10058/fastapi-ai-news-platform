from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from toutiao_backend.config.db_conf import create_tables
from toutiao_backend.config.logging_conf import setup_logging
from toutiao_backend.config.settings import get_settings
from toutiao_backend.routers import ai, favorite, history, news, users
from toutiao_backend.utils.exception_handlers import register_exception_handlers

settings = get_settings()
setup_logging(settings.debug)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="AI 掘金头条后端",
    description="AI 掘金头条项目后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "AI 掘金头条后端已启动"}


app.include_router(users.router)
app.include_router(news.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)
