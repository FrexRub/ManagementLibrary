from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
import asyncio

from src.models.user import User
from src.core.config import COOKIE_NAME

username = "Bob"
email = "Bob@mail.ru"


async def test_connect(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
):
    response = await client.get("/")
    assert response.status_code == 200


async def test_authorization_user(
    event_loop: asyncio.AbstractEventLoop, client: AsyncClient, test_user_admin: User
):
    response = await client.post(
        "/api/users/login",
        json={"email": "testuser@example.com", "password": "1qaz!QAZ"},
    )

    assert response.status_code == 202
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_create_user(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
    db_session: AsyncSession,
):
    user = {
        "username": username,
        "email": email,
    }
    cookies = {COOKIE_NAME: token_admin}

    response = await client.post(
        "/api/users/create",
        json=user,
        cookies=cookies,
    )

    stmt = select(User).filter(User.email == email)
    res: Result = await db_session.execute(stmt)
    user_db: User = res.scalar_one_or_none()

    assert response.status_code == 201
    assert user_db.email == email


async def test_user_unique_email(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
):
    user = {
        "username": username + "Lee",
        "email": email,
    }
    cookies = {COOKIE_NAME: token_admin}

    response = await client.post(
        "/api/users/create",
        json=user,
        cookies=cookies,
    )
    assert response.json() == {"detail": "The email address is already in use"}
    assert response.status_code == 400


async def test_user_put(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
    db_session: AsyncSession,
):
    stmt = select(User).filter(User.email == email)
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()
    user_id: str = str(user_db.id)

    user = {"username": "Lena", "email": "smirnova@mail.ru"}
    cookies = {COOKIE_NAME: token_admin}

    response = await client.put(
        f"/api/users/{user_id}/",
        json=user,
        cookies=cookies,
    )

    stmt = select(User).filter(User.email == "smirnova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()

    assert response.status_code == 200
    assert response.json()["username"] == "Lena"
    assert response.json()["email"] == "smirnova@mail.ru"
    assert user_db.email == "smirnova@mail.ru"


async def test_user_patch(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
    db_session: AsyncSession,
):
    stmt = select(User).filter(User.email == "smirnova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()
    user_id: str = str(user_db.id)

    user = {"email": "ivanova@mail.ru"}
    cookies = {COOKIE_NAME: token_admin}

    response = await client.patch(
        f"/api/users/{user_id}/",
        json=user,
        cookies=cookies,
    )

    stmt = select(User).filter(User.email == "ivanova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()

    assert response.status_code == 200
    assert response.json()["username"] == "Lena"
    assert response.json()["email"] == "ivanova@mail.ru"
    assert user_db.email == "ivanova@mail.ru"


async def test_user_delete(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
    db_session: AsyncSession,
):
    stmt = select(User).filter(User.email == "ivanova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()
    user_id: str = str(user_db.id)

    cookies = {COOKIE_NAME: token_admin}
    response = await client.delete(f"/api/users/{user_id}/", cookies=cookies)

    stmt = select(User).filter(User.email == "ivanova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()

    assert response.status_code == 204
    assert user_db is None
