from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookBaseSchemas(BaseModel):
    title: str = Field(max_length=100)
    author: str = Field(max_length=100)
    release_date: Optional[int] = Field(None, description="Число длиной 4 цифры (от 1000 до 9999)")
    isbn: Optional[str] = Field(None, max_length=17)
    count: int = Field(default=1, ge=1)

    @field_validator('release_date')
    def validate_length(cls, val):
        if val is not None:
            if not (1000 <= val <= 9999):
                raise ValueError("Число должно быть 4-значным")
        return val


class BookUpdateSchemas(BookBaseSchemas):
    pass


class BookUpdatePartialSchemas(BookUpdateSchemas):
    title: Optional[str] = None
    author: Optional[str] = None
    release_date: Optional[int] = None
    isbn: Optional[str] = None
    count: Optional[int] = None

    @field_validator('release_date')
    def validate_length(cls, val):
        if val is not None:
            if not (1000 <= val <= 9999):
                raise ValueError("Число должно быть 4-значным")
        return val


class BookCreateSchemas(BookBaseSchemas):
    pass


class OutBookSchemas(BookBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)
