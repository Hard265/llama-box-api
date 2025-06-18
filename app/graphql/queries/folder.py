from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.orm import Session
import strawberry
from app.database import get_db
from app.models.folder import Folder

from app.graphql.types import FolderType


@strawberry.type
class FolderQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FolderType]:
        db: Session = next(get_db())
        folder = db.query(Folder).get(id)
        if folder:
            return folder
        return None

    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[FolderType]:
        db = next(get_db())
        folders = db.query(Folder).all()
        return folders
