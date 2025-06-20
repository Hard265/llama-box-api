from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.user import User as UserSchema, UserCreate
from app.models.user import User
from app.schemas.auth import TokenData
from app.core.auth import get_current_user, get_hash
from app.database import get_db

router = APIRouter()


@router.post("", response_model=UserSchema)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can not register with this email",
        )
    hashed_password = get_hash(data.password)
    user = User(email=data.email, password=hashed_password)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
