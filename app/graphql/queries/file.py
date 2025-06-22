from typing import Optional, Sequence
from uuid import UUID

import strawberry

from app.database import get_db
from app.graphql.errors import FileOperationError
from app.graphql.types import FileType
from app.services.file import get_user_file, get_user_files


@strawberry.type
class FileQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FileType]:
        user = info.context.get("user")
        if not user:
            raise FileOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        file = get_user_file(db=db, user_id=UUID(user.sub), id=id)
        if not file:
            raise FileOperationError("File does not exist", "NOT_FOUND")

        return file

    @strawberry.field
    def get_all(
        self, info: strawberry.Info, folder_id: Optional[UUID] = None
    ) -> Sequence[FileType]:
        user = info.context.get("user")
        if not user:
            raise FileOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        files = list(get_user_files(db=db, user_id=UUID(user.sub), folder_id=folder_id))
        return files
