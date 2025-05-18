from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class ReceivingBook(Base):
    __table_args__ = (
        UniqueConstraint("reader_id", "book_id", name="idx_unique_reader_book"),
    )
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    borrow_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    return_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)

    book: Mapped["Book"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="books")

    def __repr__(self) -> str:
        return (
            f"{self.book_id}, {self.reader_id}, {self.borrow_date}, {self.return_date}"
        )
