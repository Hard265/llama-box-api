from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.user import (
    create_user as create_user_service,
    get_user_by_sub,
    change_password as change_password_service,
)
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserPasswordChange,
)
from app.schemas.auth import TokenData
from app.core.auth import get_current_user
from app.database import get_db

router = APIRouter()


@router.post("", response_model=UserSchema)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(data, db)


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_user_by_sub(str(current_user.sub) if current_user.sub else None, db)


@router.post("/me/change-password")
async def change_password(
    data: UserPasswordChange,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return change_password_service(
        str(current_user.sub) if current_user.sub else None, data, db
    )
