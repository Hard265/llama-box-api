import os
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import strawberry
from strawberry.file_uploads import Upload
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.graphql.types import FileType, FileUpdateInput
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
            if error:
                raise StrawberryGraphQLError(
                    message="Could not create file", extensions={"code": error}
                )
            return file_instance
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while creating file",
                extensions={"code": "INTERNAL_ERROR"},
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
            if error:
                raise StrawberryGraphQLError(
                    message="Could not delete file", extensions={"code": error}
                )
            return FileDeleteResult(success=True, message="File deleted successfully")
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while deleting file",
                extensions={"code": "INTERNAL_ERROR"},
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
            if error:
                raise StrawberryGraphQLError(
                    message="Could not update file", extensions={"code": error}
                )
            return file_obj
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while updating file",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
