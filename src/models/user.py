from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.library import ReceivingBook


class User(Base):
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[Optional[str]]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    books: Mapped[list["ReceivingBook"]] = relationship(back_populates="user")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, email={self.email!r})"

    def repr(self) -> str:
        return str(self)
