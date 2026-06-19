#!/bin/sh
set -e

echo "[backend] Waiting for database readiness..."

/app/.venv/bin/python - <<'PY'
import asyncio
import logging

from sqlalchemy import text

from toutiao_backend.config.db_conf import AsyncSessionLocal, create_tables

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [entrypoint] %(message)s")
logger = logging.getLogger("entrypoint")


async def wait_for_database() -> None:
    for attempt in range(1, 61):
        try:
            await create_tables()
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            logger.info("Database is ready after %s attempt(s)", attempt)
            return
        except Exception as exc:
            logger.warning("Database not ready yet (attempt %s/60): %s", attempt, exc)
            await asyncio.sleep(2)

    raise RuntimeError("Database is not ready after 60 attempts")


asyncio.run(wait_for_database())
PY

echo "[backend] Launching uvicorn..."
exec /app/.venv/bin/uvicorn toutiao_backend.main:app --host 0.0.0.0 --port 8000
