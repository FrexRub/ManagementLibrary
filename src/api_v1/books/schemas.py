from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BookBaseSchemas(BaseModel):
    title: str = Field(max_length=100)
    author: str = Field(max_length=100)
    release_date: date
    isbn: str = Field(max_length=17)
    count: int = Field(ge=1)


class BookUpdateSchemas(BookBaseSchemas):
    pass


class BookUpdatePartialSchemas(BookUpdateSchemas):
    title: Optional[str] = None
    author: Optional[str] = None
    release_date: Optional[date] = None
    isbn: Optional[str] = None
    count: Optional[int] = None


class BookCreateSchemas(BookBaseSchemas):
    pass


class OutBookSchemas(BookBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)
