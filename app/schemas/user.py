from uuid import UUID
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: str | UUID
    email: EmailStr | None = None
    is_active: bool = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str
