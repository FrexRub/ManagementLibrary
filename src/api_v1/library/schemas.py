from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_serializer, Field, ConfigDict


class ReceivingBaseSchemas(BaseModel):
    reader_id: int = Field(..., description="ID пользователя, который берет книгу")
    book_id: int = Field(..., description="ID книги, которую берут")


class ReceivingCreateSchemas(ReceivingBaseSchemas):
    pass


class ReceivingReturnSchemas(ReceivingBaseSchemas):
    pass


class OutReceivingSchemas(ReceivingBaseSchemas):
    borrow_date: datetime

    @field_serializer("borrow_date")
    def serialize_date_of_issue(self, dt: datetime, _info):
        return dt.strftime("%d-%b-%Y")


class ReceivingResultSchemas(BaseModel):
    result: str


class RecevingBookUserSchemas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    author: str
    release_date: Optional[int]
    isbn: Optional[str]
