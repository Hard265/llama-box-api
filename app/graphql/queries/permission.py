from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.exceptions import StrawberryGraphQLError
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
            raise StrawberryGraphQLError(
                message="Invalid permission ID format", extensions={"code": "BAD_INPUT"}
            )

        user = info.context.get("user")
        db = next(get_db())
        try:
            permission = (
                db.query(FilePermission)
                .options(
                    joinedload(FilePermission.file), joinedload(FilePermission.user)
                )
                .filter(
                    FilePermission.id == permission_id,
                    FilePermission.user_id == UUID(user.sub),
                )
                .one_or_none()
            )
            if not permission:
                raise StrawberryGraphQLError(
                    message="Permission does not exist", extensions={"code": "NOT_FOUND"}
                )
            return permission
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving file permission",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def get_by_file(
        self, info: strawberry.Info, file_id: str
    ) -> Sequence[FilePermissionType]:
        try:
            file_uuid = UUID(file_id)
        except ValueError:
            raise StrawberryGraphQLError(
                message="Invalid file ID format", extensions={"code": "BAD_INPUT"}
            )

        user = info.context.get("user")
        db = next(get_db())
        try:
            permissions = (
                db.query(FilePermission)
                .options(
                    joinedload(FilePermission.file), joinedload(FilePermission.user)
                )
                .filter(
                    FilePermission.file_id == file_uuid,
                    FilePermission.user_id == UUID(user.sub),
                )
                .all()
            )
            return permissions
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving file permissions",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def getAll(self, info: strawberry.Info) -> Sequence[FilePermissionType]:
        user = info.context.get("user")
        db = next(get_db())
        try:
            permissions = (
                db.query(FilePermission)
                .options(
                    joinedload(FilePermission.file), joinedload(FilePermission.user)
                )
                .filter(FilePermission.user_id == UUID(user.sub))
            )
            return list(permissions)
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving file permissions",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()


@strawberry.type
class FolderPermissionQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: str) -> Optional[FolderPermissionType]:
        try:
            permission_id = UUID(id)
        except ValueError:
            raise StrawberryGraphQLError(
                message="Invalid permission ID format", extensions={"code": "BAD_INPUT"}
            )

        user = info.context.get("user")
        db = next(get_db())
        try:
            permission = (
                db.query(FolderPermission)
                .options(
                    joinedload(FolderPermission.folder),
                    joinedload(FolderPermission.user),
                )
                .filter(
                    FolderPermission.id == permission_id,
                    FolderPermission.user_id == UUID(user.sub),
                )
                .one_or_none()
            )
            if not permission:
                raise StrawberryGraphQLError(
                    message="Permission does not exist", extensions={"code": "NOT_FOUND"}
                )
            return permission
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving folder permission",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def get_by_folder(
        self, info: strawberry.Info, folder_id: str
    ) -> Sequence[FolderPermissionType]:
        try:
            folder_uuid = UUID(folder_id)
        except ValueError:
            raise StrawberryGraphQLError(
                message="Invalid folder ID format", extensions={"code": "BAD_INPUT"}
            )

        user = info.context.get("user")
        db = next(get_db())
        try:
            permissions = (
                db.query(FolderPermission)
                .options(
                    joinedload(FolderPermission.folder),
                    joinedload(FolderPermission.user),
                )
                .filter(
                    FolderPermission.folder_id == folder_uuid,
                    FolderPermission.user_id == UUID(user.sub),
                )
                .all()
            )
            return permissions
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving folder permissions",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def getAll(self, info: strawberry.Info) -> Sequence[FolderPermissionType]:
        user = info.context.get("user")
        db = next(get_db())
        try:
            permissions = (
                db.query(FolderPermission)
                .options(
                    joinedload(FolderPermission.folder),
                    joinedload(FolderPermission.user),
                )
                .filter(FolderPermission.user_id == UUID(user.sub))
            )
            return list(permissions)
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving folder permissions",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
