from typing import Optional, Sequence
from uuid import UUID

import strawberry
from sqlalchemy.exc import SQLAlchemyError
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.graphql.types import FileType
from app.services.file import get_user_file, get_user_files
from sqlalchemy.orm import Session


@strawberry.type
class FileQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FileType]:
        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            file_instance, error = get_user_file(db=db, user_id=UUID(user.sub), id=id)
            if error:
                raise StrawberryGraphQLError(
                    message="File not found", extensions={"code": error}
                )
            if not file_instance:
                raise StrawberryGraphQLError(
                    message="Unable to retrieve file",
                    extensions={"code": "INTERNAL_ERROR"},
                )
            return file_instance
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while retrieving file",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def get_all(
        self, info: strawberry.Info, folder_id: Optional[UUID] = None
    ) -> Sequence[FileType]:
        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            files = get_user_files(db=db, user_id=UUID(user.sub), folder_id=folder_id)
            return files
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while retrieving files",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
