from datetime import datetime

from pydantic import BaseModel, field_serializer, Field


class ReceivingBaseSchemas(BaseModel):
    reader_id: int = Field(..., description="ID пользователя, который берет книгу")
    book_id: int = Field(..., description="ID книги, которую берут")


class ReceivingCreateSchemas(ReceivingBaseSchemas):
    pass


class ReceivingReturnSchemas(ReceivingBaseSchemas):
    pass


class OutReceivingSchemas(ReceivingBaseSchemas):
    borrow_date: datetime
    # return_date: datetime

    @field_serializer("borrow_date")
    def serialize_date_of_issue(self, dt: datetime, _info):
        return dt.strftime("%d-%b-%Y")

    # @field_serializer("return_date")
    # def serialize_date_of_return(self, dt: datetime, _info):
    #     return dt.strftime("%d-%b-%Y")
