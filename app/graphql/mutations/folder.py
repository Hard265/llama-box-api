from uuid import UUID
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Optional
from app.database import get_db
from app.models.folder import Folder
from app.models.permission import FolderPermission
from app.schemas.folder import FolderCreate, FolderUpdate
from app.graphql.types import (
    FolderCreationInput,
    FolderType,
    FolderUpdateInput,
    DeleteResponse,
)
from app.models.permission import RoleEnum
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.folder import create_folder, update_folder, delete_folder
from app.graphql.errors import FolderOperationError


@strawberry.type
class FolderMutations:
    @strawberry.mutation
    def create(self, info: strawberry.Info, input: FolderCreationInput) -> FolderType:
        user = info.context.get("user")
        try:
            data = FolderCreate(name=input.name, parent_id=input.parent_id)
        except ValidationError as exc:
            raise FolderOperationError("Invalid input data", "INVALID_INPUT") from exc

        db = next(get_db())
        try:
            folder, error = create_folder(
                db=db, folder_data=data, user_id=UUID(user.sub)
            )
            if error == "NOT_FOUND":
                raise FolderOperationError(
                    f"Parent folder with ID {data.parent_id} does not exist",
                    "NOT_FOUND",
                )
            elif error == "INTEGRITY_ERROR":
                raise FolderOperationError(
                    "Database integrity error", "INTEGRITY_ERROR"
                )
            elif error == "INTERNAL_ERROR":
                raise FolderOperationError("Internal server error", "INTERNAL_ERROR")
            elif not folder:
                raise FolderOperationError(
                    "Unknown error occurred during folder creation", "INTERNAL_ERROR"
                )
            return folder
        except SQLAlchemyError:
            db.rollback()
            raise FolderOperationError(
                "Database error occurred while creating folder", "INTERNAL_ERROR"
            )

    @strawberry.mutation
    def update(
        self, info: strawberry.Info, id: UUID, input: FolderUpdateInput
    ) -> FolderType:
        user = info.context.get("user")
        try:
            data = FolderUpdate(id=id, **input.__dict__)
        except ValidationError as exc:
            raise FolderOperationError(
                "Invalid input data for folder update", "INVALID_INPUT"
            ) from exc
        db = next(get_db())
        try:
            folder, error = update_folder(db, UUID(user.sub), data, input)
            if error == "FORBIDDEN":
                raise FolderOperationError(
                    "You do not have permission to update this folder", "FORBIDDEN"
                )
            elif error == "NOT_FOUND":
                raise FolderOperationError("Folder not found for update", "NOT_FOUND")
            elif not folder:
                raise FolderOperationError(
                    "Unknown error occurred during folder update", "INTERNAL_ERROR"
                )
            return folder
        except SQLAlchemyError:
            db.rollback()
            raise FolderOperationError(
                "Database error occurred while updating folder", "INTERNAL_ERROR"
            )

    @strawberry.mutation
    def delete(
        self,
        info: strawberry.Info,
        id: UUID,
    ) -> DeleteResponse:
        user = info.context.get("user")
        db = next(get_db())
        try:
            success, error = delete_folder(db, UUID(user.sub), id)
            if error == "FORBIDDEN":
                raise FolderOperationError(
                    "Only the owner can delete this folder", "FORBIDDEN"
                )
            elif error == "NOT_FOUND":
                raise FolderOperationError("Folder not found", "NOT_FOUND")
            elif not success:
                raise FolderOperationError(
                    "Unknown error occurred during folder deletion", "INTERNAL_ERROR"
                )
            return DeleteResponse(success=True, message="Folder deleted successully")
        except SQLAlchemyError:
            db.rollback()
            raise FolderOperationError(
                "Database error occurred while deleting folder", "INTERNAL_ERROR"
            )
