from strawberry.permission import BasePermission


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"
    error_extensions = {"code": "UNAUTHENTICATED", "msg": "Missing or invalid token"}

    def has_permission(self, source, info, **kwargs) -> bool:
        user = info.context.get("user")
        return bool(user)
