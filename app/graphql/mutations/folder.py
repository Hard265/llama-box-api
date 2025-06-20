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
from app.models.permission import FolderPermission, RoleEnum
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


@strawberry.type
class FolderMutations:
    @strawberry.mutation
    def create(self, info: strawberry.Info, input: FolderCreationInput) -> FolderType:
        user = info.context.get("user")
        if not user or not hasattr(user, "sub"):
            raise ValueError("User not authenticated")
        sub = user.sub

        try:
            data = FolderCreate(name=input.name, parent_id=input.parent_id)
        except ValidationError as e:
            raise ValueError(f"Invalid input: {str(e)}")

        with next(get_db()) as db:
            if data.parent_id:
                parent = db.query(Folder).filter(Folder.id == data.parent_id).first()
                if not parent:
                    raise ValueError(
                        f"Parent folder with ID {data.parent_id} does not exist"
                    )

            try:
                folder = Folder(name=data.name, parent_id=data.parent_id)
                db.add(folder)
                db.flush()
                permission = FolderPermission(
                    user_id=UUID(sub), folder_id=folder.id, role=RoleEnum.owner
                )
                db.add(permission)
                db.commit()
                db.refresh(folder)
                db.refresh(permission)
                return folder
            except IntegrityError as e:
                db.rollback()
                logger.error(f"Integrity error creating folder: {str(e)}")
                raise ValueError(
                    "Folder creation failed: likely duplicate name or invalid parent"
                ) from e
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Database error creating folder: {str(e)}")
                raise Exception("Database error occurred") from e

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
