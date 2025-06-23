from uuid import UUID
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Optional
from app.database import get_db
from app.models.folder import Folder
from app.schemas.folders import FolderCreate, FolderUpdate
from app.graphql.types import (
    FolderCreationInput,
    FolderType,
    FolderUpdateInput,
    DeleteResponse,
)
from app.models.permission import RoleEnum
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.folder import create_folder
from app.graphql.errors import FolderOperationError


@strawberry.type
class FolderMutations:
    @strawberry.mutation
    def create(self, info: strawberry.Info, input: FolderCreationInput) -> FolderType:
        user = info.context.get("user")
        if not user:
            raise FolderOperationError("Authentication required", "UNAUTHENTICATED")
        try:
            data = FolderCreate(name=input.name, parent_id=input.parent_id)
        except ValidationError as exc:
            raise FolderOperationError("Invalid input data", "INVALID_INPUT") from exc

        with next(get_db()) as db:
            if data.parent_id:
                parent = db.query(Folder).filter(Folder.id == data.parent_id).first()
                if not parent:
                    raise ValueError(
                        f"Parent folder with ID {data.parent_id} does not exist"
                    )

            try:
                folder = create_folder(db=db, folder_data=data, user_id=UUID(user.sub))
                if not folder:
                    raise FolderOperationError("Folder does not exist", "NOT_FOUND")
                return folder
            except IntegrityError:
                db.rollback()
                raise FolderOperationError(
                    "Database integrity error", "INTEGRITY_ERROR"
                )

            except SQLAlchemyError:
                db.rollback()
                raise FolderOperationError("Internal server error", "INTERNAL_ERROR")

    @strawberry.mutation
    def update(self, info: strawberry.Info, input: FolderUpdateInput) -> FolderType:
        try:
            data = FolderUpdate(**input.__dict__)
        except ValidationError as e:
            raise Exception(e.json())
        db = next(get_db())
        try:
            folder: Optional[Folder] = db.query(Folder).get(data.id)
            if not folder:
                raise Exception("Folder doesn't exist")

            for field in FolderUpdate.model_fields:
                if field == "id":
                    continue
                if field in input.__dict__:
                    setattr(folder, field, getattr(data, field, None))

            db.commit()
            db.refresh(folder)
            return folder
        except SQLAlchemyError:
            db.rollback()
            raise Exception("Internal server error")

    @strawberry.mutation
    def delete(
        self,
        _: strawberry.Info,
        id: UUID,
    ) -> DeleteResponse:
        db = next(get_db())
        try:
            folder_obj = db.query(Folder).get(id)
            if not folder_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
                )

            db.delete(folder_obj)
            db.commit()
            return DeleteResponse(success=True, message="Folder deleted successully")
        except SQLAlchemyError:
            db.rollback()
            raise Exception("Internal server error")
