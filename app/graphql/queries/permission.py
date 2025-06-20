from typing import Optional, Sequence
from uuid import UUID

from graphql import GraphQLError
import strawberry
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.graphql.types import FilePermissionType, FolderPermissionType
from app.models.permission import FilePermission, FolderPermission


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
                .options(joinedload(FilePermission.file), joinedload(FilePermission.user))
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
            permissions = (
                db.query(FilePermission)
                .options(joinedload(FilePermission.file), joinedload(FilePermission.user))
                .filter(FilePermission.user_id == UUID(user.sub))
            )
            return list(permissions)
        finally:
            db.close()


@strawberry.type
class FolderPermissionQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: str) -> Optional[FolderPermissionType]:
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
                db.query(FolderPermission)
                .options(joinedload(FolderPermission.folder), joinedload(FolderPermission.user))
                .filter(
                    FolderPermission.id == permission_id,
                    FolderPermission.user_id == UUID(user.sub),
                )
                .one_or_none()
            )
            if not permission:
                raise GraphQLError("Permission does not exist")
            return permission
        finally:
            db.close()

    @strawberry.field
    def getAll(self, info: strawberry.Info) -> Sequence[FolderPermissionType]:
        user = info.context.get("user")
        if not user:
            raise GraphQLError("Authentication required")
        db = next(get_db())
        try:
            permissions = (
                db.query(FolderPermission)
                .options(joinedload(FolderPermission.folder), joinedload(FolderPermission.user))
                .filter(FolderPermission.user_id == UUID(user.sub))
            )
            return list(permissions)
        finally:
            db.close()