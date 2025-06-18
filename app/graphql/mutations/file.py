import os
import aiofiles
import magic
from pathlib  import Path
from uuid import UUID, uuid4
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.file_uploads import Upload
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Optional
from app.database import get_db
from app.models.file import File

from app.graphql.types import FileType, DeleteResponse

MEDIA_ROOT = "media"
os.makedirs(MEDIA_ROOT, exist_ok=True)

@strawberry.type
class FileMutations:

    @strawberry.mutation
    async def create(
        self, 
        _, 
        file: Upload, 
        name: Optional[str] = None
    ) -> FileType:

        filename_uuid = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(MEDIA_ROOT, filename_uuid)

        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024):
                await out_file.write(chunk)

        async with aiofiles.open(file_path, "rb") as f:
            sample = await f.read(2048)
            mime_type = magic.from_buffer(sample, mime=True)

        extension = Path(file.filename).suffix.lower().lstrip(".")

        db = next(get_db())
        try:
            file_instance = File(
                name=file.filename,
                file=file_path,
                mime_type=mime_type,
                size=file.size,
                ext = extension
            )
            db.add(file_instance)
            db.commit()
            db.refresh(file_instance)
            return file_instance
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
            file_obj = db.query(File).get(id)
            if not file_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

            if os.path.exists(file_obj.file):
                os.remove(file_obj.file)

            db.delete(file_obj)
            db.commit()
            return DeleteResponse(success=True, message="File deleted successully")
        except SQLAlchemyError:
            db.rollback()
            raise Exception("Internal server error")

