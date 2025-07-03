from uuid import UUID
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.schemas.folder import FolderCreate, FolderUpdate
from app.graphql.types import (
    FolderCreationInput,
    FolderType,
    FolderUpdateInput,
    DeleteResponse,
)
from app.services.folder import create_folder, update_folder, delete_folder


@strawberry.type
class FolderMutations:
    @strawberry.mutation
    def create(self, info: strawberry.Info, input: FolderCreationInput) -> FolderType:
        user = info.context.get("user")
        try:
            data = FolderCreate(name=input.name, parent_id=input.parent_id)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                "Invalid input data", extensions={"code": "INVALID_INPUT"}
            ) from exc

        db = next(get_db())
        try:
            folder, error = create_folder(
                db=db, folder_data=data, user_id=UUID(user.sub)
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not create folder", extensions={"code": error}
                )
            return folder
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while creating folder",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.mutation
    def update(
        self, info: strawberry.Info, id: UUID, input: FolderUpdateInput
    ) -> FolderType:
        user = info.context.get("user")
        try:
            data = FolderUpdate(id=id, **input.__dict__)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                "Invalid input data for folder update",
                extensions={"code": "INVALID_INPUT"},
            ) from exc
        db = next(get_db())
        try:
            folder, error = update_folder(db, UUID(user.sub), data, input)
            if error:
                raise StrawberryGraphQLError(
                    message="Could not update folder", extensions={"code": error}
                )
            return folder
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while updating folder",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

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
            if error:
                raise StrawberryGraphQLError(
                    message="Could not delete folder", extensions={"code": error}
                )
            return DeleteResponse(success=True, message="Folder deleted successully")
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while deleting folder",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
