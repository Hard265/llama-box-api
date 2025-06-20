from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import Token, TokenRequest
from app.database import get_db
from app.models.user import User
from app.core.auth import verify_hash, create_access_token

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
    return {"access_token": access_token, "token_type": "bearer"}
