import os
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import strawberry
from strawberry.file_uploads import Upload

from app.database import get_db
from app.graphql.types import FileType, FileUpdateInput
from app.graphql.errors import FileOperationError
from app.services.file import update_file, delete_file, create_file


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
        db = next(get_db())
        try:
            file_instance, error = await create_file(
                db=db, user_id=UUID(user.sub), file=file, folder_id=folder_id
            )
            if error == "INVALID_INPUT":
                raise FileOperationError("Invalid folder ID format", "INVALID_INPUT")
            elif error == "PERMISSION_DENIED":
                raise FileOperationError("No permission to upload", "PERMISSION_DENIED")
            elif error == "FAILED_SAVE":
                raise FileOperationError("Failed to save file", "INTERNAL_ERROR")
            elif error == "FILE_EXISTS":
                raise FileOperationError("File already exists", "FILE_EXISTS")
            elif error == "INTERNAL_ERROR":
                raise FileOperationError("Internal server error", "INTERNAL_ERROR")
            elif not file_instance:
                raise FileOperationError("Unable to create file", "INTERNAL_ERROR")
            return file_instance
        except SQLAlchemyError:
            db.rollback()
            raise FileOperationError(
                "Database error occurred while creating file", "INTERNAL_ERROR"
            )
        finally:
            db.close()

    @strawberry.mutation
    def delete(
        self,
        info: strawberry.Info,
        id: UUID,
    ) -> FileDeleteResult:
        user = info.context.get("user")
        db = next(get_db())
        try:
            success, error = delete_file(db=db, user_id=UUID(user.sub), file_id=id)
            if error == "NOT_FOUND":
                raise FileOperationError("File not found", "NOT_FOUND")
            elif error == "PERMISSION_DENIED":
                raise FileOperationError("No permission to delete", "PERMISSION_DENIED")
            elif error == "FAILED_DELETE":
                raise FileOperationError(
                    "Failed to delete physical file", "INTERNAL_ERROR"
                )
            elif error == "INTERNAL_ERROR":
                raise FileOperationError("Internal server error", "INTERNAL_ERROR")
            elif not success:
                raise FileOperationError(
                    "Unknown error occurred during file deletion", "INTERNAL_ERROR"
                )
            return FileDeleteResult(success=True, message="File deleted successfully")
        except SQLAlchemyError:
            db.rollback()
            raise FileOperationError(
                "Database error occurred while deleting file", "INTERNAL_ERROR"
            )
        finally:
            db.close()

    @strawberry.mutation
    def update(
        self,
        info: strawberry.Info,
        id: UUID,
        input: FileUpdateInput,
    ) -> FileType:
        user = info.context.get("user")
        db = next(get_db())
        try:
            file_obj, error = update_file(
                db=db,
                user_id=UUID(user.sub),
                file_id=id,
                name=input.name,
                folder_id=input.folder_id,
            )
            if error == "NOT_FOUND":
                raise FileOperationError("File not found or no permission", "NOT_FOUND")
            elif error == "INTEGRITY_ERROR":
                raise FileOperationError("Integrity error", "INTEGRITY_ERROR")
            elif error == "INTERNAL_ERROR":
                raise FileOperationError("Database error", "INTERNAL_ERROR")
            elif not file_obj:
                raise FileOperationError("Unable to update file", "INTERNAL_ERROR")
            return file_obj
        except SQLAlchemyError:
            db.rollback()
            raise FileOperationError(
                "Database error occurred while updating file", "INTERNAL_ERROR"
            )
        finally:
            db.close()
