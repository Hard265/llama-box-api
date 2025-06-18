from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    sub: str
    email: EmailStr | None = None
