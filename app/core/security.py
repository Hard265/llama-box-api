import os
from typing import Optional
from jose import jwt
from app.schemas.auth import TokenData
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 60)

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY is missing from enviromental variables")

def decode_token(token: str) -> TokenData:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        email: Optional[str] = payload.get("email")
        if email is None:
            raise credential_exception
        token_data = TokenData(email=email)
    return token_data
