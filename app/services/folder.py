from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.folder import Folder
from app.models.permission import FolderPermission, RoleEnum
from app.schemas.folders import FolderCreate


def get_folder(db: Session, user_id: UUID, id: UUID):
    """
    Get user's folder of the provided id
    """
    query = (
        db.query(Folder)
        .join(FolderPermission)
        .filter(FolderPermission.user_id == user_id, Folder.id == id)
        .first()
    )
    return query


def get_folders(db: Session, user_id: UUID, parent_id: Optional[UUID] = None):
    """
    Get user's folders filtered by parent_id.

    Args:
        parent_id: None for root folders, UUID string for subfolders
    """
    query = (
        db.query(Folder)
        .join(FolderPermission)
        .filter(FolderPermission.user_id == user_id)
    )

    return (
        query.filter(Folder.parent_id.is_(None))
        if parent_id is None
        else query.filter(Folder.parent_id == parent_id)
    )


def create_folder(db: Session, folder_data: FolderCreate, user_id: UUID):
    folder = Folder(name=folder_data.name, parent_id=folder_data.parent_id)
    db.add(folder)
    db.flush()

    permission = FolderPermission(
        user_id=user_id, folder_id=folder.id, role=RoleEnum.owner
    )
    db.add(permission)
    db.commit()
    db.refresh(folder)
    db.refresh(permission)
    return folder
