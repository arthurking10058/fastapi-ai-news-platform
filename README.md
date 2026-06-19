# FastAPI AI News Platform

一个前后端分离新闻平台项目。

项目包含新闻分类、新闻列表与详情、收藏、浏览历史，以及一个优先查询本地新闻数据的 AI 问答接口。

## 项目截图能力

- 用户注册 / 登录
- 新闻分类、列表、详情
- 收藏与浏览历史
- Redis 缓存热点新闻数据
- AI 问答优先命中本地新闻库，查不到时再返回兜底结果
- Docker 一键启动完整演示环境

## 技术栈

- 后端：FastAPI、SQLAlchemy Async ORM、MySQL、Redis
- 前端：Vue 3、Vite、Pinia、Vue Router、Vant
- AI 接口：OpenAI-compatible Chat Completions
- 工具链：`uv`、`pytest`、`npm`、`docker compose`

## 目录结构

```text
fastapi_first/
|- toutiao_backend/      # FastAPI 后端
|- xwzx-news/            # Vue 3 前端
|- tests/                # 后端接口测试
|- docker-compose.yml    # 本地演示编排
|- .env.example
|- pyproject.toml
`- README.md
```

## 环境要求

- Python 3.13+
- Node.js 18+，推荐 Node.js 20+
- MySQL 8.x
- Redis 7.x
- Docker Desktop（如果使用 Docker 演示）

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
VITE_API_BASE_URL=http://localhost
```

说明：

- 本地前后端分开启动时，前端建议把 `VITE_API_BASE_URL` 设为 `http://127.0.0.1:8000`
- Docker 演示时，前端镜像会在构建阶段写入 `http://localhost:8000`
- 不配置 `AI_API_KEY` 也可以运行大部分基础功能，但 AI 路由只能走数据库分支或兜底结果

## 本地开发说明

### 1. 安装后端依赖

```powershell
uv sync
```

### 2. 启动 Python 虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 启动后端

```powershell
uv run uvicorn toutiao_backend.main:app --reload
```

后端地址：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- 根路由：`http://127.0.0.1:8000/`

### 4. 启动前端

```powershell
Set-Location .\xwzx-news
npm install
npm run dev
```

前端地址：

- `http://localhost:5173`

### 5. 本地演示推荐顺序

如果你是为了快速演示项目，而不是日常开发，推荐按下面顺序准备：

1. 先确认本地 MySQL 和 Redis 已启动
2. 执行演示数据重建脚本
3. 启动后端
4. 启动前端
5. 使用演示账号登录并走一遍首页、详情、收藏、历史、AI 问答

## 演示数据重建

项目根目录下可以重复执行演示数据脚本：

```powershell
uv run python .\toutiao_backend\scripts\seed_demo_data.py --reset
```

这条命令会：

- 补齐内置演示分类
- 重建用于演示的新闻数据
- 刷新 AI 问答可命中的热点新闻样本
- 使用前端 `public/demo-images/` 下的稳定本地图资源
- 保留已有用户账号与公共分类，只重建已知演示新闻记录

适用场景：

- 演示前快速恢复稳定数据
- 本地改动后重新整理首页与详情页展示内容
- 验证 AI 的数据库优先问答分支

## Docker 演示

### 一键启动

在项目根目录执行：

```powershell
docker compose up --build
```

默认会启动：

- `mysql`：MySQL 8.4
- `redis`：Redis 7
- `seed`：一次性演示数据初始化服务
- `backend`：FastAPI 后端
- `frontend`：Nginx 托管的 Vue 前端

启动后访问：

- 前端：`http://localhost`
- 后端：`http://localhost:8000`
- Swagger：`http://localhost:8000/docs`
- MySQL：`127.0.0.1:3306`
- Redis：`127.0.0.1:6379`

### Docker 演示特点

- 后端会等待 MySQL 就绪后再启动
- `seed` 容器会先写入演示数据，成功后后端才会启动
- 前端镜像内已写入默认后端地址，无需再单独配置浏览器代理

### Docker 演示账号

- 用户名：`admin`
- 密码：`123456`

### Docker 演示内容

首次启动后，演示环境通常包含：

- 多个新闻分类
- 首页和详情页可用的演示新闻
- 一组稳定的本地图封面
- 演示账号、示例收藏与浏览历史

说明：

- Docker 演示环境采用本地 `demo-images` 作为新闻配图示意资源，用于保证容器环境下图片展示稳定性。
- 与主机历史数据中的外链真实图片效果存在差异，但不影响首页、详情、收藏、历史与 AI 问答等核心功能验收。

### 重新初始化 Docker 演示环境

如果你想完全重置容器和数据库卷，再重新生成演示数据：

```powershell
docker compose down -v
docker compose up --build
```

这一步会清空 Docker 卷中的 MySQL 数据，适合正式演示前做一次干净重建。

## 前端请求层说明

前端请求统一收口在：

```text
xwzx-news/src/utils/request.js
```

它负责：

- 统一 `baseURL`
- 优先从 Pinia 当前状态读取 token
- 回退读取持久化登录态
- 自动注入 `Authorization: Bearer <token>`
- 统一提取接口错误消息

收藏、历史、AI 问答和用户信息等模块都走这一套共享请求客户端。

## 日志与异常处理

后端已统一接入基础日志和全局异常处理：

- 启动时根据 `DEBUG` 设置日志级别
- Redis 缓存异常会走日志而不是直接 `print`
- `HTTPException`、数据库异常、未处理异常都会返回统一响应结构
- `DEBUG=true` 时，异常响应会额外带上 traceback 等调试信息
- 生产或演示模式下默认不会把敏感堆栈直接暴露给前端

统一返回结构示例：

```json
{
  "code": 500,
  "message": "服务器内部错误",
  "data": null
}
```

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
- 收藏与浏览历史流程
- AI 数据库优先分支
- finance / fiscal / sports 等自然问法分支

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
