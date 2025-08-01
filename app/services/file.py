import os
from pathlib import Path
from uuid import UUID, uuid4
from typing import Optional
import aiofiles
import magic
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload, Session, selectinload
from strawberry.file_uploads import Upload
from PIL import Image
import io
from app.models.file import File
from app.models.folder import Folder
from app.models.permission import FilePermission, FolderPermission, RoleEnum

from app.schemas.file import CreateFile

MEDIA_ROOT = "media"
os.makedirs(MEDIA_ROOT, exist_ok=True)


def create_file(db: Session, user_id: UUID, file_data: CreateFile):
    try:
        parent_folder_id = file_data.folder_id
        if parent_folder_id:
            folder = db.query(Folder).get(parent_folder_id)
            if not folder:
                return None, "NOT_FOUND"

            permission = (
                db.query(FolderPermission)
                .filter(
                    FolderPermission.folder_id == parent_folder_id,
                    FolderPermission.user_id == user_id,
                    FolderPermission.role.in_([RoleEnum.owner, RoleEnum.editor]),
                )
                .first()
            )
            if not permission:
                return None, "PERMISSION_DENIED"

        file_instance = File(
            name=file_data.name,
            file=file_data.file,
            folder_id=parent_folder_id,
            mime_type=file_data.mime_type,
            size=file_data.size,
            ext=file_data.ext,
        )
        db.add(file_instance)
        db.flush()

        permission = FilePermission(
            user_id=user_id, file_id=file_instance.id, role=RoleEnum.owner
        )
        db.add(permission)
        db.commit()

        file_instance = (
            db.query(File)
            .options(
                joinedload(File.folder),
                selectinload(File.permissions).selectinload(FilePermission.user),
                selectinload(File.links),
            )
            .filter(File.id == file_instance.id)
            .first()
        )
        if not file_instance:
            return None, "INTERNAL_ERROR"

        return file_instance, None
    except IntegrityError:
        db.rollback()
        return None, "FILE_EXISTS"
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"


async def save_uploaded_file(file: Upload) -> tuple[str, str, str, int]:
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


def delete_file(db: Session, user_id: UUID, file_id: UUID):
    try:
        file_obj = db.query(File).get(file_id)
        if not file_obj:
            return False, "NOT_FOUND"
        permission = (
            db.query(FilePermission)
            .filter(
                FilePermission.file_id == file_obj.id,
                FilePermission.user_id == user_id,
                FilePermission.role == RoleEnum.owner,
            )
            .first()
        )
        if not permission:
            return False, "PERMISSION_DENIED"
        if os.path.exists(file_obj.file):
            try:
                os.remove(file_obj.file)
            except OSError:
                return False, "FAILED_DELETE"
        db.query(FilePermission).filter(FilePermission.file_id == file_id).delete()
        db.delete(file_obj)
        db.commit()
        return True, None
    except SQLAlchemyError:
        db.rollback()
        return False, "INTERNAL_ERROR"


def get_user_file(db: Session, user_id: UUID, id: UUID):
    """
    Get user's file of the provided id
    """
    query = (
        db.query(File)
        .options(
            joinedload(File.folder),
            selectinload(File.permissions).selectinload(FilePermission.user),
            selectinload(File.links),
        )
        .join(FilePermission)
        .filter(FilePermission.user_id == user_id, File.id == id)
        .first()
    )
    if not query:
        return None, "NOT_FOUND"
    return query, None


def generate_thumbnail(file_path: str, size: tuple[int, int] = (128, 128)):
    try:
        img = Image.open(file_path)
        img.thumbnail(size)
        thumb_io = io.BytesIO()
        img.save(thumb_io, format="PNG")
        thumb_io.seek(0)
        return thumb_io, None
    except Exception as e:
        return None, str(e)


def get_user_files(db: Session, user_id: UUID, folder_id: Optional[UUID] = None):
    """
    Get user's files filtered by folder_id.

    Args:
        parent_id: None for root folders, UUID string for subfolders
    """
    query = (
        db.query(File)
        .options(
            selectinload(File.folder).selectinload(Folder.permissions),
            selectinload(File.permissions).selectinload(FilePermission.user),
            selectinload(File.links),
        )
        .join(FilePermission)
        .filter(FilePermission.user_id == user_id)
    )

    return (
        query.filter(File.folder_id.is_(None))
        if folder_id is None
        else query.filter(File.folder_id == folder_id)
    ).all()


def update_file(
    db: Session,
    user_id: UUID,
    file_id: UUID,
    name: Optional[str] = None,
):
    file_obj = (
        db.query(File)
        .join(FilePermission)
        .filter(
            File.id == file_id,
            FilePermission.user_id == user_id,
            FilePermission.role == RoleEnum.owner,
        )
        .first()
    )
    if not file_obj:
        return None, "NOT_FOUND"
    if name is not None:
        file_obj.name = name
    try:
        db.commit()
        db.refresh(file_obj)
        return file_obj, None
    except IntegrityError:
        db.rollback()
        return None, "INTEGRITY_ERROR"
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"
