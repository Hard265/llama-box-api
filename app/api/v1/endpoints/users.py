from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.core.security import decode_token

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user=Depends(decode_token)):
    return current_user
