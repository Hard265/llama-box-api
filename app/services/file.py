from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.file import File
from app.models.permission import FilePermission


def get_user_file(db: Session, user_id: UUID, id: UUID):
    """
    Get user's file of the provided id
    """
    query = (
        db.query(File)
        .join(FilePermission)
        .filter(FilePermission.user_id == user_id, File.id == id)
        .first()
    )
    return query


def get_user_files(db: Session, user_id: UUID, folder_id: Optional[UUID] = None):
    """
    Get user's files filtered by folder_id.

    Args:
        parent_id: None for root folders, UUID string for subfolders
    """
    query = (
        db.query(File).join(FilePermission).filter(FilePermission.user_id == user_id)
    )

    return (
        query.filter(File.folder_id.is_(None))
        if folder_id is None
        else query.filter(File.folder_id == folder_id)
    )
