import logging
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
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting application and ensuring database tables exist")
    await create_tables()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="FastAPI AI News Platform",
    description="A FastAPI backend for the AI news demo platform.",
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
    return {"message": "FastAPI AI News Platform backend is running."}


app.include_router(users.router)
app.include_router(news.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)
