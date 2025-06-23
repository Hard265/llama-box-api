from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.folder import Folder
from app.models.permission import FolderPermission, RoleEnum
from app.schemas.folder import FolderCreate


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
    """
    Create a folder and assign owner permission.
    Returns (folder, error_code) where error_code is None or "NOT_FOUND" or "INTEGRITY_ERROR".
    """
    from app.models.folder import Folder
    from app.models.permission import FolderPermission, RoleEnum

    # If parent_id is provided, check if parent exists
    if folder_data.parent_id:
        parent = db.query(Folder).filter(Folder.id == folder_data.parent_id).first()
        if not parent:
            return None, "NOT_FOUND"

    try:
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
        return folder, None
    except IntegrityError:
        db.rollback()
        return None, "INTEGRITY_ERROR"
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"


def update_folder(db: Session, user_id: UUID, folder_update_schema, input_data):
    """
    Update a folder if the user has owner or editor permission.
    Returns the updated folder or raises an appropriate exception.
    """
    from app.models.folder import Folder
    from app.models.permission import FolderPermission, RoleEnum

    id = folder_update_schema.id

    # Check if user has owner or editor permission for this folder
    folder = (
        db.query(Folder)
        .join(FolderPermission)
        .filter(
            Folder.id == id,
            FolderPermission.user_id == user_id,
            FolderPermission.role.in_([RoleEnum.owner, RoleEnum.editor]),
        )
        .first()
    )
    if not folder:
        # Check if the user is at least a viewer
        viewer_folder = (
            db.query(Folder)
            .join(FolderPermission)
            .filter(
                Folder.id == id,
                FolderPermission.user_id == user_id,
                FolderPermission.role == RoleEnum.viewer,
            )
            .first()
        )
        if viewer_folder:
            return None, "FORBIDDEN"
        else:
            return None, "NOT_FOUND"

    for field in folder_update_schema.model_fields:
        if field == "id":
            continue
        if field in input_data.__dict__:
            setattr(folder, field, getattr(folder_update_schema, field, None))

    db.commit()
    db.refresh(folder)
    return folder, None


def delete_folder(db: Session, user_id: UUID, folder_id: UUID):
    """
    Delete a folder if the user is the owner.
    Returns (success, error_code) where error_code is None, "FORBIDDEN", or "NOT_FOUND".
    """
    from app.models.folder import Folder
    from app.models.permission import FolderPermission, RoleEnum

    folder_obj = (
        db.query(Folder)
        .join(FolderPermission)
        .filter(
            Folder.id == folder_id,
            FolderPermission.user_id == user_id,
            FolderPermission.role == RoleEnum.owner,
        )
        .first()
    )
    if not folder_obj:
        # Check if folder exists at all
        exists = db.query(Folder).filter(Folder.id == folder_id).first()
        if exists:
            return False, "FORBIDDEN"
        else:
            return False, "NOT_FOUND"

    db.delete(folder_obj)
    db.commit()
    return True, None
