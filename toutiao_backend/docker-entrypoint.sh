#!/bin/sh
set -e

/app/.venv/bin/python - <<'PY'
import asyncio

from sqlalchemy import text

from toutiao_backend.config.db_conf import AsyncSessionLocal, create_tables


async def wait_for_database() -> None:
    for _ in range(60):
        try:
            await create_tables()
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return
        except Exception:
            await asyncio.sleep(2)

    raise RuntimeError("Database is not ready")


asyncio.run(wait_for_database())
PY

/app/.venv/bin/python - <<'PY'
from toutiao_backend.config.db_conf import create_tables
import asyncio

asyncio.run(create_tables())
PY

exec /app/.venv/bin/uvicorn toutiao_backend.main:app --host 0.0.0.0 --port 8000
