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
    FolderCopyInput,
    FolderCopyResponse,
    FolderMoveInput,
)
from app.services.folder import create_folder, update_folder, delete_folder, get_folder
from app.services.copy import CopyService
from app.services.move import move_folders


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
            data = FolderUpdate(id=id, name=input.name, starred=input.starred)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                "Invalid input data for folder update",
                extensions={"code": "INVALID_INPUT"},
            ) from exc
        db = next(get_db())
        try:
            folder, error = update_folder(db, UUID(user.sub), data)
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

    @strawberry.mutation
    def copy(self, info: strawberry.Info, input: FolderCopyInput) -> FolderCopyResponse:
        user = info.context.get("user")
        db = next(get_db())
        try:
            copied_folders = []
            for source_id in input.source_ids:
                source_folder = get_folder(db, UUID(user.sub), source_id)
                if not source_folder:
                    raise StrawberryGraphQLError(
                        f"Source folder with id {source_id} not found",
                        extensions={"code": "NOT_FOUND"},
                    )

                destination_parent = None
                if input.destination_parent_id:
                    destination_parent = get_folder(
                        db, UUID(user.sub), input.destination_parent_id
                    )
                    if not destination_parent:
                        raise StrawberryGraphQLError(
                            "Destination folder not found",
                            extensions={"code": "NOT_FOUND"},
                        )

                copy_service = CopyService(db)
                copied_folder = copy_service.copy_folder(
                    source_folder=source_folder,
                    destination_parent=destination_parent,
                    user=user,
                )
                copied_folders.append(copied_folder)

            db.commit()
            return FolderCopyResponse(folders=copied_folders)
        except PermissionError as e:
            db.rollback()
            raise StrawberryGraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while copying folder",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.mutation
    def move(self, info: strawberry.Info, input: FolderMoveInput) -> FolderCopyResponse:
        user = info.context.get(
            "user")
        db = next(get_db())
        try:
            source_folders = []
            for source_id in input.source_ids:
                source_folder = get_folder(db, UUID(user.sub), source_id)
                if not source_folder:
                    raise StrawberryGraphQLError(
                        f"Source folder with id {source_id} not found",
                        extensions={"code": "NOT_FOUND"},
                    )
                source_folders.append(source_folder)

            destination_folder = get_folder(db, UUID(user.sub), input.destination_folder_id)
            if not destination_folder:
                raise StrawberryGraphQLError(
                    "Destination folder not found", extensions={"code": "NOT_FOUND"}
                )

            moved_folders = move_folders(
                db,
                source_folders=source_folders,
                destination_folder=destination_folder,
                user=user,
            )
            db.commit()
            return FolderCopyResponse(folders=moved_folders)
        except (PermissionError, ValueError) as e:
            db.rollback()
            raise StrawberryGraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while moving folder",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
