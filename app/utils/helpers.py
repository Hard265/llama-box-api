import os
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
import magic
from sqlalchemy.orm import Session
from strawberry.file_uploads import Upload

from app.models.permission import FilePermission, FolderPermission, RoleEnum

MEDIA_ROOT = "media"
os.makedirs(MEDIA_ROOT, exist_ok=True)


async def save_uploaded_file(file: Upload) -> tuple[str, str, str, int]:
    """Save uploaded file and return (file_path, mime_type, extension, size)"""
    filename_uuid = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(MEDIA_ROOT, filename_uuid)

    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(1024):
            await out_file.write(chunk)

    async with aiofiles.open(file_path, "rb") as f:
        sample = await f.read(2048)
        mime_type = magic.from_buffer(sample, mime=True)

    extension = Path(file.filename).suffix.lower().lstrip(".")
    return file_path, mime_type, extension, file.size


def check_folder_permission(
    db: Session, user_id: UUID, folder_id: UUID, required_role: RoleEnum
) -> bool:
    """Check if user has required permission for folder"""
    permission = (
        db.query(FolderPermission)
        .filter(
            FolderPermission.folder_id == folder_id,
            FolderPermission.user_id == user_id,
            FolderPermission.role == required_role,
        )
        .first()
    )
    return permission is not None


def check_file_permission(
    db: Session, user_id: UUID, file_id: UUID, required_role: RoleEnum
) -> bool:
    """Check if user has required permission for file"""
    permission = (
        db.query(FilePermission)
        .filter(
            FilePermission.file_id == file_id,
            FilePermission.user_id == user_id,
            FilePermission.role == required_role,
        )
        .first()
    )
    return permission is not None
