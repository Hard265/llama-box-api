from typing import Optional, Sequence
from uuid import UUID
import strawberry
from app.database import get_db
from app.models.file import File

from app.graphql.types import FileType


@strawberry.type
class FileQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FileType]:
        db = next(get_db())
        file = db.query(File).get(id)
        if file:
            return file
        return None

    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[FileType]:
        db = next(get_db())
        files = db.query(File).all()
        return files
