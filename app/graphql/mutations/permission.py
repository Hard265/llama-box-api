from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.graphql.types import FilePermissionType, FolderPermissionType, Role
from app.services.permission import (
    create_folder_permission,
    update_folder_permission,
    delete_folder_permission,
    create_file_permission,
    update_file_permission,
    delete_file_permission,
)
from app.schemas.permission import (
    CreateFolderPermission,
    UpdateFolderPermission,
    CreateFilePermission,
    UpdateFilePermission,
)


@strawberry.input
class CreateFolderPermissionInput:
    id: UUID
    email: str
    role: Role


@strawberry.input
class UpdateFolderPermissionInput:
    id: UUID
    permission_id: UUID
    role: Role


@strawberry.type
class FolderPermissionMutations:
    @strawberry.mutation
    def create(
        self, info: strawberry.Info, input: CreateFolderPermissionInput
    ) -> FolderPermissionType:
        user = info.context.get("user")
        try:
            data = CreateFolderPermission(**input.__dict__)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                exc.title, extensions={"code": "BAD_USER_INPUT"}
            ) from exc

        db = next(get_db())
        try:
            permission, error = create_folder_permission(
                db=db, user_id=UUID(user.sub), data=data
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not create permission", extensions={"code": error}
                )
            return permission
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()

    @strawberry.mutation
    def update(
        self, info: strawberry.Info, input: UpdateFolderPermissionInput
    ) -> FolderPermissionType:
        user = info.context.get("user")
        try:
            data = UpdateFolderPermission(**input.__dict__)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                exc.title, extensions={"code": "BAD_USER_INPUT"}
            ) from exc

        db = next(get_db())
        try:
            permission, error = update_folder_permission(
                db=db, user_id=UUID(user.sub), data=data
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not update permission", extensions={"code": error}
                )
            return permission
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()

    @strawberry.mutation
    def delete(self, info: strawberry.Info, permission_id: UUID) -> bool:
        user = info.context.get("user")
        db = next(get_db())
        try:
            success, error = delete_folder_permission(
                db=db, user_id=UUID(user.sub), permission_id=permission_id
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not delete permission", extensions={"code": error}
                )
            return success
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()


@strawberry.input
class CreateFilePermissionInput:
    id: UUID
    email: str
    role: Role


@strawberry.input
class UpdateFilePermissionInput:
    id: UUID
    permission_id: UUID
    role: Role


@strawberry.type
class FilePermissionMutations:
    @strawberry.mutation
    def create(
        self, info: strawberry.Info, input: CreateFilePermissionInput
    ) -> FilePermissionType:
        user = info.context.get("user")
        try:
            data = CreateFilePermission(**input.__dict__)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                exc.title, extensions={"code": "BAD_USER_INPUT"}
            ) from exc

        db = next(get_db())
        try:
            permission, error = create_file_permission(
                db=db, user_id=UUID(user.sub), data=data
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not create permission", extensions={"code": error}
                )
            return permission
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()

    @strawberry.mutation
    def update(
        self, info: strawberry.Info, input: UpdateFilePermissionInput
    ) -> FilePermissionType:
        user = info.context.get("user")
        try:
            data = UpdateFilePermission(**input.__dict__)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                exc.title, extensions={"code": "BAD_USER_INPUT"}
            ) from exc

        db = next(get_db())
        try:
            permission, error = update_file_permission(
                db=db, user_id=UUID(user.sub), data=data
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not update permission", extensions={"code": error}
                )
            return permission
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()

    @strawberry.mutation
    def delete(self, info: strawberry.Info, permission_id: UUID) -> bool:
        user = info.context.get("user")
        db = next(get_db())
        try:
            success, error = delete_file_permission(
                db=db, user_id=UUID(user.sub), permission_id=permission_id
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not delete permission", extensions={"code": error}
                )
            return success
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()
