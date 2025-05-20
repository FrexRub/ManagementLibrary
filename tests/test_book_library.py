import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
import asyncio

from src.models.user import User
from src.models.book import Book
from src.core.config import COOKIE_NAME
from src.api_v1.books.schemas import BookCreateSchemas
from src.api_v1.library.schemas import ReceivingCreateSchemas


@pytest.mark.parametrize("title, author, count",
                         [("Гарри Поттер и философский камень", "Джоан Кэтлин Роулинг", 1),
                          ("Тайна мертвого ректора", "Виктор Дашкевич", 4),
                          ("Бюро бракованных решений", "Максим Суворов", 7),
                          ("Капитанская дочка", "Александр Пушкин", 5),
                          ("Анна Каренина", "Лев Толстой", 2)])
async def test_add_new_book(
        title: str, author: str, count: int,
        event_loop: asyncio.AbstractEventLoop,
        client: AsyncClient,
        token_admin: str,
):
    book: BookCreateSchemas = BookCreateSchemas(
        title=title,
        author=author,
        count=count,
    )
    cookies = {COOKIE_NAME: token_admin}

    response = await client.post(
        "/api/books/new",
        json=book.model_dump(),
        cookies=cookies,
    )
    assert response.status_code == 201


async def test_add_new_book_bad(
        event_loop: asyncio.AbstractEventLoop,
        client: AsyncClient,
        token_admin: str,
):
    book: BookCreateSchemas = BookCreateSchemas(
        title="title",
        author="author",
        isbn="isbn",
        count=1,
    )
    cookies = {COOKIE_NAME: token_admin}
    response = await client.post(
        "/api/books/new",
        json=book.model_dump(),
        cookies=cookies,
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid ISBN format"}


async def test_add_new_book_bad_user(
        event_loop: asyncio.AbstractEventLoop,
        client: AsyncClient,
):
    book: BookCreateSchemas = BookCreateSchemas(
        title="title",
        author="author",
        isbn="isbn",
        count=1,
    )
    response = await client.post(
        "/api/books/new",
        json=book.model_dump(),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


async def test_books_in_db(
        event_loop: asyncio.AbstractEventLoop,
        db_session: AsyncSession,
):
    stmt = select(Book)
    res: Result = await db_session.execute(stmt)
    books_db = res.scalars().all()

    assert len(books_db) == 5


@pytest.mark.parametrize("reader_id, book_id", [(2, 1), (2, 2), (2, 3)])
async def test_borrow_book(
        reader_id: int, book_id: int,
        event_loop: asyncio.AbstractEventLoop,
        client: AsyncClient,
        token_admin: str,
        test_user: User,
):
    borrow: ReceivingCreateSchemas = ReceivingCreateSchemas(
        reader_id=reader_id,
        book_id=book_id,
    )
    cookies = {COOKIE_NAME: token_admin}

    response = await client.post(
        "/api/library/borrow",
        json=borrow.model_dump(),
        cookies=cookies,
    )
    assert response.status_code == 201


async def test_borrow_book_more_3(
        event_loop: asyncio.AbstractEventLoop,
        client: AsyncClient,
        token_admin: str,
        test_user: User,
):
    borrow: ReceivingCreateSchemas = ReceivingCreateSchemas(
        reader_id=2,
        book_id=4,
    )
    cookies = {COOKIE_NAME: token_admin}

    response = await client.post(
        "/api/library/borrow",
        json=borrow.model_dump(),
        cookies=cookies,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user has 3 books"}


async def test_borrow_book_not_in_library(
        event_loop: asyncio.AbstractEventLoop,
        client: AsyncClient,
        token_admin: str,
        test_user: User,
):
    borrow: ReceivingCreateSchemas = ReceivingCreateSchemas(
        reader_id=1,
        book_id=10,
    )
    cookies = {COOKIE_NAME: token_admin}

    response = await client.post(
        "/api/library/borrow",
        json=borrow.model_dump(),
        cookies=cookies,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Not find book"}
