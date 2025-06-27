import os
from typing import Dict, Optional, Any
import logging
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

from app.schemas.auth import TokenData  # Assuming this exists as per your original code

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Secret keys for access and refresh tokens
ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
if ACCESS_SECRET_KEY is None or REFRESH_SECRET_KEY is None:
    raise RuntimeError("ACCESS_SECRET_KEY or REFRESH_SECRET_KEY is missing from environment variables")

# Algorithm validation
ALLOWED_ALGORITHMS = {"HS256", "HS384", "HS512"}
ALGORITHM = os.getenv("ALGORITHM", "HS256")
if ALGORITHM not in ALLOWED_ALGORITHMS:
    raise RuntimeError(f"Invalid algorithm: {ALGORITHM}")

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_hash(secret: str, hash: str) -> bool:
    """Verify a secret against its hash."""
    return pwd_context.verify(secret, hash)

def get_hash(secret: str) -> str:
    """Generate a hash for a secret."""
    return pwd_context.hash(secret)

def create_access_token(data: Dict[str, Any]) -> str:
    """Create an access token with a 'type' claim."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token with a 'type' claim."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_refresh_token(token: str) -> TokenData:
    """Decode and validate a refresh token."""
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        sub: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if sub is None or token_type != "refresh":
            logger.error(f"Invalid refresh token: sub={sub}, type={token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        return TokenData(sub=sub)
    except JWTError as e:
        logger.error(f"Refresh token decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate an access token and return user data."""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        sub: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if sub is None or token_type != "access":
            logger.error(f"Invalid access token: sub={sub}, type={token_type}")
            raise credential_exception
        return TokenData(sub=sub)
    except JWTError as e:
        logger.error(f"Access token decode error: {str(e)}")
        raise credential_exception

def get_current_user_from_request(request: Request) -> Optional[TokenData]:
    """Extract and validate an access token from a request header (optional auth)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    scheme, token = get_authorization_scheme_param(auth_header)
    if not scheme or not token or scheme.lower() != "bearer":
        return None

    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        sub: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if sub is None or token_type != "access":
            logger.debug(f"Invalid optional token: sub={sub}, type={token_type}")
            return None
        return TokenData(sub=sub)
    except JWTError:
        logger.debug("Optional token decode error")
        return None

