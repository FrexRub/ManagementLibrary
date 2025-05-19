import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.book import Book
from src.api_v1.books.schemas import (
    BookUpdateSchemas,
    BookUpdatePartialSchemas,
    BookCreateSchemas,
)
from src.core.exceptions import ErrorInData, ExceptDB
from src.core.config import configure_logging

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_book(session: AsyncSession, book_id: int) -> Optional[Book]:
    logger.info("Getting genre by id %d" % book_id)
    return await session.get(Book, book_id)


async def create_book(session: AsyncSession, book_in: BookCreateSchemas) -> Book:
    logger.info("Start create new book")
    try:
        book: Book = Book(**book_in.model_dump())
    except ValueError as exc:
        logger.exception("Error in value %s", exc)
        raise ErrorInData(exc)
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB(exc)
    else:
        session.add(book)
        await session.commit()
        logger.info("New book create")
        return book


async def update_book_db(
    session: AsyncSession,
    book: Book,
    book_update: Union[BookUpdateSchemas, BookUpdatePartialSchemas],
    partial: bool = False,
) -> Book:
    logger.info("Start update book")
    try:
        for name, value in book_update.model_dump(exclude_unset=partial).items():
            setattr(book, name, value)
        await session.commit()
    except ValueError as exc:
        logger.exception("Error in value %s", exc)
        raise ErrorInData(exc)
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB(exc)
    return book


async def delete_book_db(session: AsyncSession, book: Book) -> None:
    logger.info("Delete book by id %d" % book.id)
    try:
        await session.delete(book)
        await session.commit()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        await session.rollback()
        raise ExceptDB(exc)


async def get_books(session: AsyncSession) -> list[Book]:
    logger.info("Getting a list of books")
    try:
        stmt = select(Book).order_by(Book.id)
        result: Result = await session.execute(stmt)
        books = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
    return list(books)
