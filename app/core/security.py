import base64
from typing import Dict

from cachetools import TTLCache
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, status
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import httpx
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED


JWKS_URL = "http://127.0.0.1:8888/.well-known/jwks.json"
JWKS_CACHE = TTLCache(maxsize=1, ttl=3600)  # cache for 1 hour
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="not-used")  # no token issuance here


async def get_jwks() -> Dict:
    if "jwks" not in JWKS_CACHE:
        async with httpx.AsyncClient() as client:
            resp = await client.get(JWKS_URL)
            resp.raise_for_status()
            JWKS_CACHE["jwks"] = resp.json()
    return JWKS_CACHE["jwks"]


async def decode_token(token: str = Depends(oauth2_scheme)) -> dict:
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Missing 'kid'")

    jwks = await get_jwks()
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unknown key ID")

    public_key = construct_rsa_key(key)
    try:
        payload = jwt.decode(token, public_key, algorithms=[key["alg"]])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def construct_rsa_key(jwk: dict):
    n = int.from_bytes(base64.urlsafe_b64decode(jwk["n"] + "=="), "big")
    e = int.from_bytes(base64.urlsafe_b64decode(jwk["e"] + "=="), "big")

    pub_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
    return pub_key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
