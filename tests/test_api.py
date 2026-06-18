from httpx import AsyncClient


async def test_register_and_login(client: AsyncClient):
    register_response = await client.post(
        "/api/user/register",
        json={"username": "user_a", "password": "123456"},
    )
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data["code"] == 200
    assert register_data["data"]["token"]
    assert register_data["data"]["userInfo"]["username"] == "user_a"

    login_response = await client.post(
        "/api/user/login",
        json={"username": "user_a", "password": "123456"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["code"] == 200
    assert login_data["data"]["token"]
    assert login_data["data"]["userInfo"]["username"] == "user_a"


async def test_news_categories_list_and_detail(client: AsyncClient):
    categories_response = await client.get("/api/news/categories")
    assert categories_response.status_code == 200
    categories_data = categories_response.json()
    assert categories_data["code"] == 200
    assert len(categories_data["data"]) >= 2

    list_response = await client.get("/api/news/list", params={"categoryId": 1, "page": 1, "pageSize": 10})
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["code"] == 200
    assert len(list_data["data"]["list"]) >= 1

    detail_response = await client.get("/api/news/detail", params={"id": 1})
    assert detail_response.status_code == 200
    detail_data = detail_response.json()
    assert detail_data["code"] == 200
    assert detail_data["data"]["id"] == 1
    assert "relatedNews" in detail_data["data"]


async def test_favorite_and_history_flow(client: AsyncClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}

    favorite_add_response = await client.post(
        "/api/favorite/add",
        json={"newsId": 1},
        headers=headers,
    )
    assert favorite_add_response.status_code == 200
    assert favorite_add_response.json()["code"] == 200

    favorite_check_response = await client.get(
        "/api/favorite/check",
        params={"newsId": 1},
        headers=headers,
    )
    assert favorite_check_response.status_code == 200
    assert favorite_check_response.json()["data"]["isFavorite"] is True

    favorite_list_response = await client.get(
        "/api/favorite/list",
        params={"page": 1, "pageSize": 10},
        headers=headers,
    )
    assert favorite_list_response.status_code == 200
    assert len(favorite_list_response.json()["data"]["list"]) == 1

    history_add_response = await client.post(
        "/api/history/add",
        json={"newsId": 1},
        headers=headers,
    )
    assert history_add_response.status_code == 200
    assert history_add_response.json()["code"] == 200

    history_list_response = await client.get(
        "/api/history/list",
        params={"page": 1, "pageSize": 10},
        headers=headers,
    )
    assert history_list_response.status_code == 200
    assert len(history_list_response.json()["data"]["list"]) == 1


async def test_ai_fallback_response(client: AsyncClient):
    response = await client.post(
        "/api/ai/chat",
        json={
            "question": "2024头条里浏览量最高的热门新闻有哪些？",
            "messages": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["source"] in {"database", "fallback", "ai"}
    assert data["data"]["answer"]


async def test_ai_natural_hot_news_question_hits_database_branch(client: AsyncClient):
    response = await client.post(
        "/api/ai/chat",
        json={
            "question": "24年最火的头条新闻是什么？",
            "messages": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["source"] in {"database", "fallback", "ai"}
    assert "根据当前数据库查询" in data["data"]["answer"]


async def test_ai_sports_news_question_queries_database(client: AsyncClient):
    response = await client.post(
        "/api/ai/chat",
        json={
            "question": "给我一篇关于运动的新闻",
            "messages": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["source"] in {"database", "fallback", "ai"}
    assert "根据当前数据库" in data["data"]["answer"] or "没有找到" in data["data"]["answer"]
