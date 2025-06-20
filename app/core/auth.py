import os
from typing import Dict, Optional
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from dotenv import load_dotenv

from app.schemas.auth import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 60)

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY is missing from enviromental variables")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_hash(secret: str, hash: str):
    return pwd_context.verify(secret, hash)


def get_hash(secret: str):
    return pwd_context.hash(secret)


def create_access_token(data: Dict[str, str | datetime]):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        sub: Optional[str] = payload.get("sub")
        if sub is None:
            raise credential_exception
        token_data = TokenData(sub=sub)
    except JWTError:
        raise credential_exception
    return token_data


def get_current_user_from_request(request: Request) -> TokenData:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise credential_exception
    scheme, token = get_authorization_scheme_param(auth_header)
    if not scheme or not token or scheme.lower() != "bearer":
        raise credential_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        sub: Optional[str] = payload.get("sub")
        if sub is None:
            raise credential_exception
        token_data = TokenData(sub=sub)
    except JWTError as e:
        raise credential_exception
    return token_data
