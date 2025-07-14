from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.graphql.types import (
    FileType,
    FileCopyInput,
    FileMoveInput,
    FileUpdateInput,
    FileCopyResponse,
)
from pydantic import ValidationError
from app.schemas.file import UpdateFile
from app.services.file import get_user_file, update_file
from app.services.folder import get_folder
from app.services.copy import CopyService
from app.services.move import move_files


@strawberry.type
class FileMutations:
    @strawberry.mutation
    def update(
        self, info: strawberry.Info, id: UUID, input: FileUpdateInput
    ) -> FileType:
        user = info.context.get("user")
        try:
            data = UpdateFile(name=input.name, starred=input.starred)
        except ValidationError as exc:
            raise StrawberryGraphQLError(
                "Invalid input data for file update",
                extensions={"code": "INVALID_INPUT"},
            ) from exc
        db = next(get_db())
        try:
            file, error = update_file(db, UUID(user.sub), id, name=data.name, starred=data.starred)
            if error:
                raise StrawberryGraphQLError(
                    message="Could not update file", extensions={"code": error}
                )
            return file
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while updating file",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.mutation
    def copy(self, info: strawberry.Info, input: FileCopyInput) -> FileCopyResponse:
        user = info.context.get("user")
        db = next(get_db())
        try:
            copied_files = []
            destination_folder = get_folder(db, UUID(user.sub), input.destination_folder_id)
            if not destination_folder:
                raise StrawberryGraphQLError(
                    "Destination folder not found", extensions={"code": "NOT_FOUND"}
                )

            for source_id in input.source_ids:
                source_file, error = get_user_file(db, UUID(user.sub), source_id)
                if error:
                    raise StrawberryGraphQLError(
                        f"Source file with id {source_id} not found",
                        extensions={"code": "NOT_FOUND"},
                    )

                copy_service = CopyService(db)
                copied_file = copy_service.copy_file(
                    source_file=source_file,
                    destination_folder=destination_folder,
                    user=user,
                )
                copied_files.append(copied_file)

            db.commit()
            return FileCopyResponse(files=copied_files)
        except PermissionError as e:
            db.rollback()
            raise StrawberryGraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while copying file",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.mutation
    def move(self, info: strawberry.Info, input: FileMoveInput) -> FileCopyResponse:
        user = info.context.get("user")
        db = next(get_db())
        try:
            source_files = []
            for source_id in input.source_ids:
                source_file, error = get_user_file(db, UUID(user.sub), source_id)
                if error:
                    raise StrawberryGraphQLError(
                        f"Source file with id {source_id} not found",
                        extensions={"code": "NOT_FOUND"},
                    )
                source_files.append(source_file)

            destination_folder = get_folder(db, UUID(user.sub), input.destination_folder_id)
            if not destination_folder:
                raise StrawberryGraphQLError(
                    "Destination folder not found", extensions={"code": "NOT_FOUND"}
                )

            moved_files = move_files(
                db,
                source_files=source_files,
                destination_folder=destination_folder,
                user=user,
            )
            db.commit()
            return FileCopyResponse(files=moved_files)
        except (PermissionError, ValueError) as e:
            db.rollback()
            raise StrawberryGraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while moving file",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()