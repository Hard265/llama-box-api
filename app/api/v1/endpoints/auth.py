from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import Token, TokenData, TokenRequest, RefreshTokenRequest
from app.database import get_db
from app.models.user import User
from app.core.auth import (
    get_current_user,
    verify_hash,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_acces_token(data: TokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_hash(data.password, user.password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})  # type: ignore
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: RefreshTokenRequest):
    token_data = decode_refresh_token(refresh_token.refresh_token)
    access_token = create_access_token(data={"sub": str(token_data.sub)})
    new_refresh_token = create_refresh_token(data={"sub": str(token_data.sub)})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)
):
    pass
