import logging
from typing import Optional
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.book import Book
from src.models.user import User
from src.models.library import ReceivingBook
from src.api_v1.library.schemas import (
    ReceivingCreateSchemas,
)
from src.core.exceptions import ErrorInData, ExceptDB
from src.core.config import configure_logging

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def create_receiving(
    session: AsyncSession,
    borrow: ReceivingCreateSchemas,
) -> ReceivingBook:
    logger.info("Start create borrow book")

    user_id: int = borrow.model_dump()["reader_id"]
    book_id: int = borrow.model_dump()["book_id"]

    book: Optional[Book] = await session.get(Book, book_id)
    if book is None:
        logger.info("Not find book")
        raise ErrorInData("Not find book")

    if book.count == 0:
        logger.info("These books are not available")
        raise ErrorInData("These books are not available")

    user: Optional[User] = await session.get(User, user_id)
    if user is None:
        logger.info("Not find user")
        raise ErrorInData("Not find user")

    stmt = select(ReceivingBook).where(
        ReceivingBook.reader_id == user_id, ReceivingBook.return_date.is_(None)
    )
    result: Result = await session.execute(stmt)
    books_user = result.scalars().all()

    logger.info(
        "Количество книг у пользователя с id: %s - %s штук" % (user_id, len(books_user))
    )

    if len(books_user) >= 3:
        logger.info("The user has 3 books")
        raise ErrorInData("The user has 3 books")

    receiving_book = ReceivingBook(
        book_id=book_id,
        reader_id=user_id,
    )

    try:
        session.add(receiving_book)
        book.count -= 1
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        logger.warning("The user already has this book")
        raise ExceptDB("The user already has this book")

    return receiving_book


async def return_receiving(
    session: AsyncSession, receiving: ReceivingCreateSchemas
) -> str:
    logger.info("Start return book in library")
    user_id: int = receiving.model_dump()["reader_id"]
    book_id: int = receiving.model_dump()["book_id"]

    stmt = select(ReceivingBook).filter(
        and_(ReceivingBook.reader_id == user_id, ReceivingBook.book_id == book_id)
    )
    result: Result = await session.execute(stmt)
    books_user: ReceivingBook = result.scalars().first()
    if books_user is None:
        logger.info("The user does not have this book")
        raise ErrorInData("The user does not have this book")

    if books_user.return_date:
        logger.info("The book has already been returned")
        raise ErrorInData("The book has already been returned")

    book: Optional[Book] = await session.get(Book, book_id)
    if book is None:
        logger.info("Not find book")
        raise ErrorInData("Not find book")

    try:
        books_user.return_date = datetime.today()
        book.count += 1
        await session.commit()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        await session.rollback()
        raise ExceptDB(exc)
    return "The book has been returned to the library"


async def get_books(session: AsyncSession, user_id: int) -> list[Book]:
    logger.info("Getting a list of books user %s" % user_id)
    try:
        stmt = (
            select(User)
            .options(selectinload(User.books).joinedload(ReceivingBook.book))
            .filter(User.id == user_id)
        )

        result: Result = await session.execute(stmt)
        user: User = result.scalars().first()

        list_book_user: list[Book] = list()
        for i_book in user.books:  # tipe: ReceivingBook
            if i_book.return_date is None:
                list_book_user.append(i_book.book)

    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB("Error in data base")

    return list_book_user
