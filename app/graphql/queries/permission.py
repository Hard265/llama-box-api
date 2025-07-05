from typing import Optional, Sequence
from uuid import UUID

import strawberry
from strawberry.exceptions import StrawberryGraphQLError
from sqlalchemy.orm import Session

from app.database import get_db
from app.graphql.types import FilePermissionType, FolderPermissionType
from app.services.permission import (
    get_all_file_permissions,
    get_all_folder_permissions,
    get_file_permission_by_id,
    get_file_permissions_by_file_id,
    get_folder_permission_by_id,
    get_folder_permissions_by_folder_id,
)


@strawberry.type
class FilePermissionQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FilePermissionType]:
        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            permission, error = get_file_permission_by_id(db, UUID(user.sub), id)
            if error:
                raise StrawberryGraphQLError(
                    message="Permission does not exist", extensions={"code": error}
                )
            return permission
        finally:
            db.close()

    @strawberry.field
    def get_by_file(
        self, info: strawberry.Info, file_id: UUID
    ) -> Sequence[FilePermissionType]:

        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            permissions, error = get_file_permissions_by_file_id(
                db, UUID(user.sub), file_id
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Unable to retrieve permissions", extensions={"code": error}
                )
            if not permissions:
                raise StrawberryGraphQLError(
                    message="Unable to process the request",
                    extensions={"code": "INTERNAL_ERROR"},
                )
            return permissions
        finally:
            db.close()

    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[FilePermissionType]:
        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            permissions, error = get_all_file_permissions(db, UUID(user.sub))
            if error:
                raise StrawberryGraphQLError(
                    message="Unable to retrieve permissions", extensions={"code": error}
                )
            if not permissions:
                raise StrawberryGraphQLError(
                    message="Unable to process the request",
                    extensions={"code": "INTERNAL_ERROR"},
                )
            return permissions
        finally:
            db.close()


@strawberry.type
class FolderPermissionQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FolderPermissionType]:

        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            permission, error = get_folder_permission_by_id(db, UUID(user.sub), id)
            if error:
                raise StrawberryGraphQLError(
                    message="Permission does not exist", extensions={"code": error}
                )
            return permission
        finally:
            db.close()

    @strawberry.field
    def get_by_folder(
        self, info: strawberry.Info, folder_id: UUID
    ) -> Sequence[FolderPermissionType]:

        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            permissions, error = get_folder_permissions_by_folder_id(
                db, UUID(user.sub), folder_id
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Unable to retrieve permissions", extensions={"code": error}
                )
            if not permissions:
                raise StrawberryGraphQLError(
                    message="Unable to process the request",
                    extensions={"code": "INTERNAL_ERROR"},
                )
            return permissions
        finally:
            db.close()

    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[FolderPermissionType]:
        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            permissions, error = get_all_folder_permissions(db, UUID(user.sub))
            if error:
                raise StrawberryGraphQLError(
                    message="Unable to retrieve permissions", extensions={"code": error}
                )
            if not permissions:
                raise StrawberryGraphQLError(
                    message="Unable to process the request",
                    extensions={"code": "INTERNAL_ERROR"},
                )
            return permissions
        finally:
            db.close()
