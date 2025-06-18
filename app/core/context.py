from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

from app.core.auth import get_current_user


async def get_context(request: Request):
    auth_header = request.headers.get("Authorization")
    user = None
    if auth_header:
        scheme, token = get_authorization_scheme_param(auth_header)
        if scheme.lower() == "bearer" and token:
            try:
                user = get_current_user(token)
            except Exception:
                pass
    return {"request": request, "user": user}
