from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.orm import Session
import strawberry

from app.database import get_db
from app.graphql.errors import FolderOperationError
from app.graphql.types import FolderType
from app.services.folder import get_folder, get_folders


@strawberry.type
class FolderQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FolderType]:
        user = info.context.get("user")
        if not user:
            raise FolderOperationError("Authentication required", "UNAUTHENTICATED")

        db: Session = next(get_db())
        folder = get_folder(db=db, user_id=UUID(user.sub), id=id)
        if not folder:
            raise FolderOperationError(
                "Folder does not exist",
                "NOT_FOUND",
            )
        return folder

    @strawberry.field
    def get_all(
        self, info: strawberry.Info, parent_id: Optional[UUID] = None
    ) -> Sequence[FolderType]:
        user = info.context.get("user")
        if not user:
            raise FolderOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        folders = list(get_folders(db=db, user_id=UUID(user.sub), parent_id=parent_id))
        return folders
