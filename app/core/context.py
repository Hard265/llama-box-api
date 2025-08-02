from fastapi import Request, Depends
from app.core.auth import get_current_user_from_request


async def get_context(request: Request, user=Depends(get_current_user_from_request)):
    if request and user:
        return {"request": request, "user": user}
    return {}
