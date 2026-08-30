import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "alice@example.com",
    "password": "password123",
    "full_name": "Alice",
}


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient) -> None:
    register = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert register.status_code == 201
    user = register.json()["data"]
    assert user["email"] == REGISTER_PAYLOAD["email"]
    assert user["is_superuser"] is False

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    assert login.status_code == 200
    tokens = login.json()["data"]
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["data"]["email"] == REGISTER_PAYLOAD["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    again = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert again.status_code == 409
    assert again.json()["code"] == 40902


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrong-pass"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    refresh_token = login.json()["data"]["refresh_token"]
    refreshed = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["data"]["access_token"]
