#!/bin/sh
set -e

python - <<'PY'
from toutiao_backend.config.db_conf import create_tables
import asyncio

asyncio.run(create_tables())
PY

exec uvicorn toutiao_backend.main:app --host 0.0.0.0 --port 8000
