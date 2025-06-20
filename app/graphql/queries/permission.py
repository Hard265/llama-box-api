from typing import Optional, Sequence
from uuid import UUID

from graphql import GraphQLError
import strawberry

from app.database import get_db
from app.graphql.types import FilePermissionType
from app.models.permission import FilePermission


@strawberry.type
class FilePermissionQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: str) -> Optional[FilePermissionType]:
        try:
            permission_id = UUID(id)
        except ValueError:
            raise GraphQLError("Invalid permission ID format")

        user = info.context.get("user")
        if not user:
            raise GraphQLError("Authentication required")
        db = next(get_db())
        try:
            permission = (
                db.query(FilePermission)
                .filter(
                    FilePermission.id == permission_id,
                    FilePermission.user_id == UUID(user.sub),
                )
                .one_or_none()
            )
            if not permission:
                raise GraphQLError("Permission does not exist")
            return permission
        finally:
            db.close()

    @strawberry.field
    def getAll(self, info: strawberry.Info) -> Sequence[FilePermissionType]:
        user = info.context.get("user")
        if not user:
            raise GraphQLError("Authentication required")
        db = next(get_db())
        try:
            permissions = db.query(FilePermission).filter(
                FilePermission.user_id == UUID(user.sub)
            )
            return list(permissions)
        finally:
            db.close()
