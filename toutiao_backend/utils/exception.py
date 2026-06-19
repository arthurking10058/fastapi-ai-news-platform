import logging
import traceback
from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

from toutiao_backend.config.settings import get_settings

logger = logging.getLogger(__name__)


def _build_error_data(request: Request, exc: Exception) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.debug:
        return None

    return {
        "error_type": type(exc).__name__,
        "error_detail": str(exc),
        "traceback": traceback.format_exc(),
        "path": str(request.url),
    }


def _json_error_response(
    status_code: int,
    message: str,
    data: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": message,
            "data": data,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code >= 500:
        logger.exception("HTTP exception on %s: %s", request.url.path, exc.detail)
    elif exc.status_code >= 400:
        logger.warning("HTTP exception on %s: %s", request.url.path, exc.detail)

    return _json_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        data=None,
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    error_msg = str(exc.orig)

    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入内容"

    logger.warning("Integrity error on %s: %s", request.url.path, error_msg)

    return _json_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=detail,
        data=_build_error_data(request, exc),
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("SQLAlchemy error on %s", request.url.path)
    return _json_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="数据库操作失败，请稍后重试",
        data=_build_error_data(request, exc),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s", request.url.path)
    return _json_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="服务器内部错误",
        data=_build_error_data(request, exc),
    )
