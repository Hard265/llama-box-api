import os
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload
import strawberry
from strawberry.file_uploads import Upload
from strawberry.exceptions import GraphQLError

from app.database import get_db
from app.models.file import File
from app.models.permission import FilePermission, FolderPermission, RoleEnum
from app.graphql.types import FileType
from app.utils.helpers import (
    check_file_permission,
    check_folder_permission,
    save_uploaded_file,
)


class FileOperationError(GraphQLError):
    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")


@strawberry.type
class FileDeleteResult:
    success: bool
    message: str


@strawberry.type
class FileMutations:
    @strawberry.mutation
    async def create(
        self, info: strawberry.Info, file: Upload, folder_id: Optional[str] = None
    ) -> FileType:
        user = info.context.get("user")
        if not user:
            raise FileOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        try:
            parent_folder_id = None
            if folder_id:
                try:
                    parent_folder_id = UUID(folder_id)
                except ValueError:
                    raise FileOperationError(
                        "Invalid folder ID format", "INVALID_INPUT"
                    )

                if not (
                    check_folder_permission(
                        db, UUID(user.sub), parent_folder_id, RoleEnum.owner
                    )
                    or check_folder_permission(
                        db, UUID(user.sub), parent_folder_id, RoleEnum.editor
                    )
                ):
                    raise FileOperationError(
                        "No permission to upload", "PERMISSION_DENIED"
                    )

            try:
                file_path, mime_type, extension, size = await save_uploaded_file(file)
            except Exception:
                raise FileOperationError("Failed to save file", "INTERNAL_ERROR")

            file_instance = File(
                name=file.filename,
                file=file_path,
                folder_id=parent_folder_id,
                mime_type=mime_type,
                size=size,
                ext=extension,
            )
            db.add(file_instance)
            db.flush()

            permission = FilePermission(
                user_id=UUID(user.sub), file_id=file_instance.id, role=RoleEnum.owner
            )
            db.add(permission)
            db.commit()

            file_instance = (
                db.query(File)
                .options(joinedload(File.folder))
                .filter(File.id == file_instance.id)
                .first()
            )
            if not file_instance:
                raise FileOperationError("Unable to create file", "INTERNAL_ERROR")
            return file_instance

        except IntegrityError:
            db.rollback()
            raise FileOperationError("File already exists", "FILE_EXISTS")

        except SQLAlchemyError:
            db.rollback()
            raise FileOperationError("Internal server error", "INTERNAL_ERROR")

        finally:
            db.close()

    @strawberry.mutation
    def delete(
        self,
        info: strawberry.Info,
        id: UUID,
    ) -> FileDeleteResult:
        user = info.context.get("user")
        if not user:
            raise FileOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        try:
            file_obj = db.query(File).get(id)
            if not file_obj:
                raise FileOperationError("File not found", "NOT_FOUND")

            if not check_file_permission(
                db, UUID(user.sub), file_obj.id, RoleEnum.owner
            ):
                raise FileOperationError("No permission to delete", "PERMISSION_DENIED")

            if os.path.exists(file_obj.file):
                try:
                    os.remove(file_obj.file)
                except OSError:
                    raise FileOperationError(
                        "Failed to delete physical file", "INTERNAL_ERROR"
                    )

            db.query(FilePermission).filter(FilePermission.file_id == id).delete()
            db.delete(file_obj)
            db.commit()

            return FileDeleteResult(success=True, message="File deleted successfully")

        except SQLAlchemyError:
            db.rollback()
            raise FileOperationError("Internal server error", "INTERNAL_ERROR")

        finally:
            db.close()
