from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.author import Author
    from src.models.library import BorrowedBooks


class Book(Base):
    __table_args__ = (CheckConstraint("count > 0", name="count_positive"),)

    title: Mapped[str] = mapped_column(String(100), index=True)
    id_author: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    release_date: Mapped[DateTime] = mapped_column(DateTime)
    isbn: Mapped[Optional[str]] = mapped_column(
        String(17),
        unique=True,
        nullable=True,
    )
    count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
    )

    author: Mapped["Author"] = relationship(back_populates="books")
    users: Mapped[list["BorrowedBooks"]] = relationship(back_populates="book")

    @validates("count")
    def validate_count(self, key, count):
        if count <= 0:
            raise ValueError("Product count must be positive")
        return count

    @validates("isbn")
    def validate_isbn(self, key, isbn):
        if isbn is not None:
            clean_isbn = isbn.replace("-", "")
            if not clean_isbn.isdigit() or len(clean_isbn) not in (10, 13):
                raise ValueError("Invalid ISBN format")
        return isbn

    def __str__(self):
        return f"Book id:{self.id} title: {self.title} release date:{self.release_date}"
