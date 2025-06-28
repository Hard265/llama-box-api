from typing import Optional, Sequence
from uuid import UUID

import strawberry

from app.database import get_db
from app.graphql.errors import FileOperationError
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
            if error == "NOT_FOUND":
                raise FileOperationError("File does not exist", "NOT_FOUND")
            elif not file_instance:
                raise FileOperationError("Unable to retrieve file", "INTERNAL_ERROR")
            return file_instance
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
        finally:
            db.close()
