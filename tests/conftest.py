import asyncio
from typing import AsyncGenerator, Generator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.database import get_async_session
from src.models.base import Base
from src.main import app
from src.models.user import User
from src.core.jwt_utils import create_hash_password

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/testdb"


@pytest_asyncio.fixture(loop_scope="session", scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL)

    print("start db_engine")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture(loop_scope="session", scope="function")
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_session] = override_get_db
    async with AsyncClient(app=app, base_url="http://") as c:
        yield c


@pytest_asyncio.fixture(loop_scope="session", scope="function")
async def test_user_admin(db_session) -> User:
    stmt = select(User).filter(User.email == "testuser@example.com")
    res: Result = await db_session.execute(stmt)
    user: User = res.scalar_one_or_none()
    if user is None:
        user_hashed_password: bytes = await create_hash_password("1qaz!QAZ")
        user: User = User(
            username="TestUser",
            email="testuser@example.com",
            hashed_password=user_hashed_password.decode(),
            is_superuser=True,
        )

        db_session.add(user)
        await db_session.commit()

    return user


@pytest_asyncio.fixture(loop_scope="session", scope="function")
async def token_admin(
        client: AsyncClient,
        test_user_admin: User,
) -> str:
    token_response = await client.post(
        "/api/users/login",
        json={"email": "testuser@example.com", "password": "1qaz!QAZ"},
    )
    token: str = token_response.json()["access_token"]
    return token


@pytest_asyncio.fixture(loop_scope="session", scope="function")
async def test_user(db_session) -> User:
    stmt = select(User).filter(User.email == "petr@mail.com")
    res: Result = await db_session.execute(stmt)
    user: User = res.scalar_one_or_none()
    if user is None:
        user: User = User(
            username="Petr",
            email="petr@mail.com",
        )

        db_session.add(user)
        await db_session.commit()

    return user
