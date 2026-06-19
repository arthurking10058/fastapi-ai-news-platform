# FastAPI AI News Platform

一个基于 `FastAPI + Vue 3` 的前后端分离新闻平台项目，包含新闻浏览、收藏、历史记录，以及一个优先查询本地新闻数据的 AI 问答能力。

这个项目更偏向完整的全栈实践：后端负责用户、新闻、缓存和 AI 问答接口，前端负责移动端风格的交互展示，Docker 环境则用于快速启动一套可演示的完整链路。

## 功能概览

- 用户注册、登录与身份状态恢复
- 新闻分类、列表、详情页
- 收藏与浏览历史
- Redis 缓存新闻数据
- AI 问答优先命中本地新闻库，再回退到模型总结或后端兜底结果
- Docker 一键启动完整演示环境

## 技术栈

### 后端

- FastAPI
- SQLAlchemy Async ORM
- MySQL
- Redis

### 前端

- Vue 3
- Vite
- Pinia
- Vue Router
- Vant

### AI

- OpenAI-compatible Chat Completions API
- 数据库优先检索 + 模型总结

### 工具链

- `uv`
- `pytest`
- `npm`
- `docker compose`

## 项目结构

```text
fastapi_first/
├─ toutiao_backend/   # FastAPI 后端
├─ xwzx-news/         # Vue 3 前端
├─ tests/             # 后端接口测试
├─ docker-compose.yml
├─ .env.example
├─ pyproject.toml
└─ README.md
```

## 项目特点

### 1. 新闻平台主流程完整

项目覆盖了一套比较完整的新闻产品主链路：

- 新闻分类切换
- 新闻列表与详情浏览
- 收藏与浏览历史
- 登录态恢复

### 2. AI 问答不是纯开放聊天

这里的 AI 问答不是单纯把问题转给模型，而是优先查本地新闻数据。

对于新闻相关问题，后端会先尝试从数据库中检索匹配内容；如果能命中，就基于本地新闻组织回答；如果没有配置 AI，或者 AI 不可用，也会返回后端可控的兜底结果。

这让 AI 路由比普通聊天接口更贴近“新闻检索助手”的定位。

### 3. Docker 演示链路可直接运行

项目已经补齐：

- MySQL / Redis / 后端 / 前端编排
- 演示数据初始化
- Docker 下的前后端访问路径

适合在本机或虚拟机里直接启动一套完整环境。

## 环境要求

- Python 3.13+
- Node.js 18+，推荐 Node.js 20+
- MySQL 8.x
- Redis 7.x
- Docker Desktop 或 Docker Engine（如果使用 Docker 方式运行）

## 环境变量

先在项目根目录创建 `.env`，可直接参考 `.env.example`。

```env
DATABASE_URL=mysql+aiomysql://root:your_password@127.0.0.1:3306/news_app?charset=utf8mb4
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
CACHE_RETRY_INTERVAL=30
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEBUG=false
AI_API_KEY=your_real_api_key
AI_MODEL=qwen-max
AI_API_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
AI_TIMEOUT=30
VITE_API_BASE_URL=http://127.0.0.1:8000
```

说明：

- 本地前后端分开启动时，前端建议使用 `http://127.0.0.1:8000`
- Docker 演示环境中，前端镜像默认构建到 `http://localhost:8000`
- 不配置 `AI_API_KEY` 时，基础功能仍可使用，AI 路由会退化为数据库结果或兜底回答

## 本地运行

### 1. 安装后端依赖

```powershell
uv sync
```

### 2. 启动后端

```powershell
.\.venv\Scripts\Activate.ps1
uv run uvicorn toutiao_backend.main:app --reload
```

后端地址：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- 根路由：`http://127.0.0.1:8000/`

### 3. 启动前端

```powershell
Set-Location .\xwzx-news
npm install
npm run dev
```

前端地址：

- `http://localhost:5173`

## 演示数据重建

项目根目录下可以重复执行演示数据脚本：

```powershell
uv run python -m toutiao_backend.scripts.seed_demo_data --reset
```

这条命令会：

- 补齐内置演示分类
- 重建用于演示的新闻数据
- 刷新 AI 问答可命中的热点新闻样本
- 使用前端 `public/demo-images/` 下的稳定本地图资源
- 保留已有用户账号与公共分类，只重建已知演示新闻记录

## Docker 运行

### 一键启动

在项目根目录执行：

```powershell
docker compose up --build
```

默认会启动：

- `mysql`
- `redis`
- `seed`
- `backend`
- `frontend`

启动后访问：

- 前端：`http://localhost`
- 后端：`http://localhost:8000`
- Swagger：`http://localhost:8000/docs`

### Docker 演示说明

- 后端会等待 MySQL 就绪后再启动
- `seed` 容器会先写入演示数据，成功后后端才会启动
- 前端镜像内已写入默认后端地址，无需再额外配置
- Docker 演示环境采用本地 `demo-images` 作为新闻配图示意资源，用于保证容器环境下图片展示稳定性

说明：

Docker 中的示意图方案和主机历史数据中的外链真实图片效果可能不同，但不影响首页、详情、收藏、历史与 AI 问答等核心功能体验。

### 演示账号

- 用户名：`admin`
- 密码：`123456`

### 重新初始化 Docker 演示环境

```powershell
docker compose down -v
docker compose up --build
```

这一步会清空 Docker 卷中的 MySQL 数据，适合需要重新生成干净演示环境时使用。

## 测试

后端接口测试位于：

```text
tests/
```

运行方式：

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

当前测试覆盖重点包括：

- 注册与登录
- 新闻分类、列表、详情
- 收藏与浏览历史
- AI 数据库优先分支
- 财经 / 财政 / 体育等自然问法分支

## API 概览

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/user/info`
- `GET /api/news/categories`
- `GET /api/news/list`
- `GET /api/news/detail`
- `GET /api/favorite/list`
- `GET /api/history/list`
- `POST /api/favorite/add`
- `GET /api/favorite/check`
- `POST /api/history/add`
- `POST /api/ai/chat`

## 适合展示的内容

如果只是正常介绍这个项目，比较自然的展示顺序是：

1. 项目结构与技术栈
2. 新闻分类、列表、详情主流程
3. 收藏与历史记录
4. AI 问答如何优先命中本地新闻数据
5. Docker 如何快速拉起完整环境

## 项目定位

这是一个以新闻平台为主体、以 AI 问答为增强能力的全栈项目。它更适合被理解为：

> 一个具备完整前后端结构、可本地运行、可 Docker 演示、并且保留继续迭代空间的 FastAPI + Vue 项目。
