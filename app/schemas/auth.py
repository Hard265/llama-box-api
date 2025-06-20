from uuid import UUID
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str | UUID


class TokenRequest(BaseModel):
    email: EmailStr
    password: str
