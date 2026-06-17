import logging
import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

from toutiao_backend.config.settings import get_settings

logger = logging.getLogger(__name__)


def _build_error_data(request: Request, exc: Exception):
    settings = get_settings()
    if not settings.debug:
        return None

    return {
        "error_type": type(exc).__name__,
        "error_detail": str(exc),
        "traceback": traceback.format_exc(),
        "path": str(request.url),
    }


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_msg = str(exc.orig)

    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"

    logger.warning("Integrity error on %s: %s", request.url, error_msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": detail,
            "data": _build_error_data(request, exc),
        },
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("SQLAlchemy error on %s", request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败，请稍后重试",
            "data": _build_error_data(request, exc),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": _build_error_data(request, exc),
        },
    )
