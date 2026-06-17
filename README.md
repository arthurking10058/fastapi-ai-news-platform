# FastAPI AI News Platform

A full-stack news platform built with FastAPI and Vue 3.

It includes user authentication, news categories and detail pages, favorites, browsing history, Redis-based cache, and an AI chat endpoint.

## Tech Stack

- Backend: FastAPI, SQLAlchemy Async ORM, MySQL, Redis
- Frontend: Vue 3, Vite, Pinia, Vue Router, Vant
- AI integration: OpenAI-compatible chat endpoint
- Tooling: `uv`, `npm`

## Features

- User register and login
- Token-based authentication
- News category, list, and detail APIs
- Favorite management
- Browsing history management
- Redis cache for frequently accessed news data
- AI chat endpoint with database-backed fallback for hot news queries

## Project Structure

```text
fastapi_first/
|- toutiao_backend/
|- xwzx-news/
|- pyproject.toml
`- README.md
```

## Prerequisites

- Python 3.13+
- Node.js 18+
- MySQL
- Redis (optional)

## Backend Setup

```powershell
uv sync
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
uv run uvicorn toutiao_backend.main:app --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Frontend Setup

```powershell
cd .\xwzx-news
npm install
npm run dev
```

- Frontend: `http://localhost:5173`

## Frontend Request Layer

Frontend requests are centralized in:

```text
xwzx-news/src/utils/request.js
```

This shared request client handles:

- unified `baseURL`
- automatic token injection from local storage
- standard `Authorization: Bearer <token>` header
- shared error message extraction

Store modules and AI chat now call this shared client instead of configuring `axios` separately in each file.

## Environment Variables

Create a local `.env` file in the project root based on `.env.example`.

```env
DATABASE_URL=mysql+aiomysql://root:your_password@127.0.0.1:3306/news_app?charset=utf8mb4
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
CACHE_RETRY_INTERVAL=30
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEBUG=false
AI_API_KEY=your_api_key
AI_MODEL=qwen-max
AI_API_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
AI_TIMEOUT=30
```

Frontend environment example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Docker

Local and demo startup:

```powershell
docker compose up --build
```

Services:

- Frontend: `http://localhost`
- Backend: `http://localhost:8000`
- MySQL: `127.0.0.1:3306`
- Redis: `127.0.0.1:6379`

The compose file starts:

- MySQL 8.4
- Redis
- a one-shot demo seed service
- FastAPI backend
- Vue frontend served by Nginx

Demo data includes:

- several news categories
- multiple news items for the home and detail pages
- a demo account: `admin` / `123456`
- a sample favorite and browsing history entry

The backend waits for MySQL during demo data seeding, then starts the app with the seeded content available for the frontend.

## Running Tests

Backend interface tests are located in:

```text
tests/
```

Run them with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Current coverage includes:

- register and login
- news categories, list, and detail
- favorite and history flows
- AI fallback response

## API Overview

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/user/info`
- `GET /api/news/categories`
- `GET /api/news/list`
- `GET /api/news/detail`
- `GET /api/favorite/list`
- `GET /api/history/list`
- `POST /api/ai/chat`
