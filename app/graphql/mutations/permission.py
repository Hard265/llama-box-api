from enum import Enum
from uuid import UUID

from graphql import GraphQLError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
import strawberry

from app.database import get_db
from app.graphql.types import FilePermissionType
from app.models.permission import FilePermission, RoleEnum
from app.schemas.permission import CreateFilePermission


class FileOperationError(GraphQLError):
    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")


@strawberry.enum
class FileRole(str, Enum):
    owner = "owner"
    viewer = "viewer"
    editor = "editor"


@strawberry.input
class FilePermissionCreateInput:
    user_id: UUID
    file_id: UUID
    role: FileRole


@strawberry.type
class FilePermissionMutations:
    @strawberry.field
    def create(
        self, info: strawberry.Info, input: FilePermissionCreateInput
    ) -> FilePermissionType:
        user = info.context.get("user")
        try:
            data = CreateFilePermission(
                user_id=input.user_id,
                file_id=input.file_id,
                role=RoleEnum(input.role.value),
            )
        except ValidationError as exc:
            print(exc)
            raise FileOperationError("Invalid input data", "INVALID_INPUT") from exc

        db: Session = next(get_db())
        try:
            is_owner = (
                db.query(FilePermission)
                .filter(
                    FilePermission.user_id == UUID(user.sub),
                    FilePermission.file_id == data.file_id,
                    FilePermission.role == RoleEnum.owner,
                )
                .first()
            )
            if not is_owner:
                raise FileOperationError(
                    "Resource does not exist or you lack permission",
                    "PERMISSION_DENIED",
                )

            existing_permission = (
                db.query(FilePermission)
                .filter(
                    FilePermission.user_id == data.user_id,
                    FilePermission.file_id == data.file_id,
                )
                .first()
            )
            if existing_permission:
                raise FileOperationError(
                    "User already has permissions for this file", "DUPLICATE_PERMISSION"
                )

            permission = FilePermission(
                user_id=data.user_id, role=input.role, file_id=data.file_id
            )
            db.add(permission)
            db.commit()

            permission = (
                db.query(FilePermission)
                .options(
                    joinedload(FilePermission.user), joinedload(FilePermission.file)
                )
                .filter(
                    FilePermission.user_id == permission.user_id,
                    FilePermission.file_id == permission.file_id,
                )
                .first()
            )
            if not permission:
                raise FileOperationError("Internal server error", "INTERNAL_ERROR")

            return permission

        except IntegrityError:
            db.rollback()
            raise FileOperationError("Database integrity error", "INTEGRITY_ERROR")

        except SQLAlchemyError:
            db.rollback()
            raise FileOperationError("Internal server error", "INTERNAL_ERROR")

        finally:
            db.close()
