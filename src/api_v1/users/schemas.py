from typing import Optional
from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

PATTERN_PASSWORD = (
    r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[0-9])(?=.*?[!"#\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_'
    r"`\{\|}~])[a-zA-Z0-9!\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_`\{\|}~]{8,}$"
)


class UserBaseSchemas(BaseModel):
    username: str = Field(min_length=2)
    email: EmailStr


class UserUpdateSchemas(BaseModel):
    pass


class UserUpdatePartialSchemas(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreateSchemas(UserBaseSchemas):
    pass


class OutUserSchemas(UserBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginSchemas(BaseModel):
    email: str
    password: str


class AuthUserSchemas(BaseModel):
    access_token: str
    token_type: str
