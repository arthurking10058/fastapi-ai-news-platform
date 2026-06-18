import asyncio
import logging
from datetime import datetime

from sqlalchemy import func, select

from toutiao_backend.config.db_conf import AsyncSessionLocal, create_tables
from toutiao_backend.models.favorite import Favorite
from toutiao_backend.models.history import History
from toutiao_backend.models.news import Category, News
from toutiao_backend.models.users import User
from toutiao_backend.utils.security import get_hash_password

logger = logging.getLogger(__name__)


DEMO_CATEGORIES = [
    {"id": 1, "name": "头条", "sort_order": 1},
    {"id": 2, "name": "社会", "sort_order": 2},
    {"id": 3, "name": "科技", "sort_order": 3},
    {"id": 4, "name": "体育", "sort_order": 4},
]

DEMO_NEWS = [
    {
        "id": 1,
        "title": "嫦娥六号返回器携月背样品着陆内蒙古",
        "description": "2024年6月25日，嫦娥六号返回器安全着陆，带回人类首批月球背面样品。",
        "content": (
            "2024年6月25日，嫦娥六号返回器在内蒙古四子王旗着陆场安全着陆，"
            "带回了人类首批月球背面样品。这次任务是中国探月工程的重要里程碑，"
            "也是全球首次实现月背采样返回。任务完成后，月球背面地质演化、"
            "撞击历史和月壤成分差异等研究都获得了更直接的样本支持。"
        ),
        "image": "https://example.com/chang-e-6.jpg",
        "author": "综合公开资料整理",
        "category_id": 1,
        "views": 9800,
        "publish_time": datetime(2024, 6, 25, 14, 0, 0),
    },
    {
        "id": 2,
        "title": "郑钦文夺得巴黎奥运会网球女单金牌",
        "description": "2024年8月3日，郑钦文成为中国首位获得奥运网球女单金牌的选手。",
        "content": (
            "2024年巴黎奥运会网球女单决赛中，郑钦文战胜对手夺得金牌，"
            "这是中国队在奥运网球女子单打项目上的历史性突破。"
            "这枚金牌也让郑钦文成为亚洲首位获得奥运网球单打金牌的运动员，"
            "在国内体育圈和社交媒体上引发了持续热议。"
        ),
        "image": "https://example.com/zheng-qinwen.jpg",
        "author": "综合公开资料整理",
        "category_id": 4,
        "views": 9300,
        "publish_time": datetime(2024, 8, 3, 21, 30, 0),
    },
    {
        "id": 3,
        "title": "《黑神话：悟空》正式发售并刷新Steam热度纪录",
        "description": "2024年8月20日，《黑神话：悟空》发售后迅速成为全球游戏热点。",
        "content": (
            "2024年8月20日，国产动作角色扮演游戏《黑神话：悟空》正式发售。"
            "游戏上线后在Steam等平台引发大量玩家涌入，成为年度最受关注的"
            "国产游戏事件之一。围绕中国神话题材、商业表现和全球传播影响力的讨论，"
            "也让它长期占据科技与游戏相关热榜。"
        ),
        "image": "https://example.com/black-myth-wukong.jpg",
        "author": "综合公开资料整理",
        "category_id": 3,
        "views": 9600,
        "publish_time": datetime(2024, 8, 20, 10, 0, 0),
    },
    {
        "id": 4,
        "title": "OpenAI 发布文生视频模型 Sora 引发热议",
        "description": "2024年2月，OpenAI 发布 Sora，推动生成式视频成为年度科技热点。",
        "content": (
            "2024年2月，OpenAI 对外展示文生视频模型 Sora。"
            "该模型可以根据文本提示生成较长且具有一致视觉效果的视频，"
            "迅速引发全球科技行业对生成式视频、内容创作与AI安全治理的广泛讨论。"
            "Sora 的公开亮相，也成为 2024 年人工智能领域最具代表性的热点事件之一。"
        ),
        "image": "https://example.com/openai-sora.jpg",
        "author": "综合公开资料整理",
        "category_id": 3,
        "views": 8900,
        "publish_time": datetime(2024, 2, 15, 9, 0, 0),
    },
    {
        "id": 5,
        "title": "苹果 Vision Pro 在美国正式开售",
        "description": "2024年2月2日，苹果 Vision Pro 上市，带动空间计算与混合现实话题升温。",
        "content": (
            "2024年2月2日，苹果 Vision Pro 正式在美国开售。"
            "作为苹果多年后推出的重要新硬件品类，这款设备引发了关于空间计算、"
            "混合现实应用场景和硬件价格门槛的持续讨论。上市初期，Vision Pro 成为"
            "全球科技媒体和开发者社区关注度极高的产品之一。"
        ),
        "image": "https://example.com/apple-vision-pro.jpg",
        "author": "综合公开资料整理",
        "category_id": 3,
        "views": 8400,
        "publish_time": datetime(2024, 2, 2, 10, 0, 0),
    },
    {
        "id": 6,
        "title": "潘展乐巴黎奥运会打破男子100米自由泳世界纪录",
        "description": "2024年巴黎奥运会上，潘展乐以破世界纪录成绩夺冠，成为中国泳坛年度高光时刻。",
        "content": (
            "2024年巴黎奥运会男子100米自由泳比赛中，潘展乐以打破世界纪录的成绩夺得金牌。"
            "这一成绩不仅刷新了项目纪录，也让中国游泳在国际舞台上再度成为焦点。"
            "比赛结果公布后，相关话题迅速登上体育热榜，成为 2024 年中国体育的重要新闻之一。"
        ),
        "image": "https://example.com/pan-zhanle.jpg",
        "author": "综合公开资料整理",
        "category_id": 4,
        "views": 9100,
        "publish_time": datetime(2024, 7, 31, 5, 30, 0),
    },
    {
        "id": 7,
        "title": "巴黎奥运会开幕式点亮塞纳河夜空",
        "description": "2024年7月26日，巴黎奥运会开幕式以塞纳河为舞台，成为全球热议焦点。",
        "content": (
            "2024年7月26日，巴黎奥运会开幕式在塞纳河沿岸举行。"
            "不同于传统体育场内开幕式，本届奥运会尝试将城市地标与大型表演结合，"
            "相关视觉设计、运动员入场方式和城市舞台概念在全球社交媒体引发了大量讨论。"
        ),
        "image": "https://example.com/paris-olympics-opening.jpg",
        "author": "综合公开资料整理",
        "category_id": 1,
        "views": 7600,
        "publish_time": datetime(2024, 7, 26, 22, 0, 0),
    },
    {
        "id": 8,
        "title": "中国代表团在巴黎奥运会以 40 金收官",
        "description": "2024年8月，中国代表团在巴黎奥运会取得40枚金牌，创造境外参赛最佳战绩之一。",
        "content": (
            "2024年巴黎奥运会落幕后，中国代表团以 40 枚金牌结束征程。"
            "这一成绩让中国体育代表团在多个项目上都收获了亮眼表现，"
            "也引发了关于竞技体育发展、重点项目突破和年轻运动员成长的广泛关注。"
        ),
        "image": "https://example.com/china-paris-2024.jpg",
        "author": "综合公开资料整理",
        "category_id": 1,
        "views": 8800,
        "publish_time": datetime(2024, 8, 11, 23, 0, 0),
    },
    {
        "id": 9,
        "title": "春节假期冰雪游热度走高带动冬季文旅消费",
        "description": "2024年初，冰雪旅游与春节出行叠加，冬季文旅消费持续升温。",
        "content": (
            "2024年春节前后，国内冰雪旅游热度持续上升，多个热门城市和景区迎来游客高峰。"
            "从滑雪场、冰雪大世界到冬季城市漫游，文旅消费和社交平台讨论度同步增长，"
            "成为年初社会民生与消费观察中的热门现象。"
        ),
        "image": "https://example.com/winter-tourism-2024.jpg",
        "author": "综合公开资料整理",
        "category_id": 2,
        "views": 6500,
        "publish_time": datetime(2024, 2, 12, 12, 0, 0),
    },
    {
        "id": 10,
        "title": "2024年人工智能应用加速落地成为科技主线",
        "description": "从大模型到多模态应用，AI 在 2024 年持续成为科技行业核心议题。",
        "content": (
            "2024年，人工智能继续保持高热度，从大模型推理能力、多模态生成，到企业应用落地，"
            "相关产品和基础设施都在快速演进。围绕模型能力、成本、应用场景与监管治理的讨论，"
            "构成了全年科技新闻中的核心主线。"
        ),
        "image": "https://example.com/ai-2024.jpg",
        "author": "综合公开资料整理",
        "category_id": 3,
        "views": 8200,
        "publish_time": datetime(2024, 9, 1, 9, 0, 0),
    },
]


async def wait_for_database() -> None:
    for _ in range(60):
        try:
            await create_tables()
            async with AsyncSessionLocal() as session:
                await session.execute(select(1))
            return
        except Exception as exc:  # pragma: no cover
            logger.info("Database not ready yet: %s", exc)
            await asyncio.sleep(2)
    raise RuntimeError("Database is not ready")


async def ensure_categories(session) -> None:
    existing_ids = set((await session.execute(select(Category.id))).scalars().all())
    categories_to_add = [Category(**item) for item in DEMO_CATEGORIES if item["id"] not in existing_ids]
    if categories_to_add:
        session.add_all(categories_to_add)
        await session.commit()


async def ensure_news(session) -> None:
    existing_titles = set((await session.execute(select(News.title))).scalars().all())
    news_to_add = [News(**item) for item in DEMO_NEWS if item["title"] not in existing_titles]
    if news_to_add:
        session.add_all(news_to_add)
        await session.commit()


async def ensure_demo_user(session) -> User | None:
    result = await session.execute(select(User).where(User.username == "admin"))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        username="admin",
        password=get_hash_password("123456"),
        nickname="演示管理员",
        bio="用于 Docker 演示的示例账号",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def ensure_demo_relations(session, user: User | None) -> None:
    if not user:
        return

    favorite_count = await session.execute(
        select(func.count(Favorite.id)).where(Favorite.user_id == user.id)
    )
    if favorite_count.scalar_one() == 0:
        session.add(Favorite(user_id=user.id, news_id=1))

    history_count = await session.execute(
        select(func.count(History.id)).where(History.user_id == user.id)
    )
    if history_count.scalar_one() == 0:
        session.add(History(user_id=user.id, news_id=1))

    await session.commit()


async def main() -> None:
    await wait_for_database()
    async with AsyncSessionLocal() as session:
        await ensure_categories(session)
        await ensure_news(session)
        user = await ensure_demo_user(session)
        await ensure_demo_relations(session, user)
    logger.info("Demo data seeded successfully")


if __name__ == "__main__":
    asyncio.run(main())
