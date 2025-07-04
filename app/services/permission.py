from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.permission import (
    CreateFolderPermission,
    UpdateFolderPermission,
    CreateFilePermission,
    UpdateFilePermission,
)
from app.models.permission import FolderPermission, FilePermission, RoleEnum
from app.services.user import get_user_by_email


def create_folder_permission(db: Session, user_id: UUID, data: CreateFolderPermission):
    """
    Creates a new permission for a user to a folder.

    Args:
        db (Session): The database session.
        user_id (UUID): The ID of the user creating the permission.
        data (CreateFolderPermission): The permission data.

    Returns:
        A tuple containing the new permission and an error code, or (None, error_code)
        if an error occurred.
    """

    # Check if the user has owner permission to the specified folder
    owner_permission = (
        db.query(FolderPermission)
        .filter(
            FolderPermission.folder_id == data.id,
            FolderPermission.user_id == user_id,
            FolderPermission.role == RoleEnum.owner,
        )
        .first()
    )

    if not owner_permission:
        return None, "FORBIDDEN"

    # Get the target user
    target_user = get_user_by_email(db, data.email)
    if not target_user:
        return None, "NOT_FOUND"

    # Create the new permission
    new_permission = FolderPermission(
        user_id=target_user.id,
        folder_id=data.id,
        role=data.role.value,
    )

    try:
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
        return new_permission, None
    except IntegrityError:
        db.rollback()
        return None, "INTEGRITY_ERROR"
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"


def update_folder_permission(db: Session, user_id: UUID, data: UpdateFolderPermission):
    """
    Updates a permission for a user to a folder.

    Args:
        db (Session): The database session.
        user_id (UUID): The ID of the user updating the permission.
        data (UpdateFolderPermission): The permission data.

    Returns:
        A tuple containing the updated permission and an error code, or (None, error_code)
        if an error occurred.
    """

    # Check if the user has owner permission to the specified folder
    owner_permission = (
        db.query(FolderPermission)
        .filter(
            FolderPermission.folder_id == data.id,
            FolderPermission.user_id == user_id,
            FolderPermission.role == RoleEnum.owner,
        )
        .first()
    )

    if not owner_permission:
        return None, "FORBIDDEN"

    permission = (
        db.query(FolderPermission).filter(FolderPermission.id == data.permission_id).first()
    )
    if not permission:
        return None, "NOT_FOUND"

    permission.role = data.role.value

    try:
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission, None
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"


def delete_folder_permission(db: Session, user_id: UUID, permission_id: UUID):
    """
    Deletes a permission for a user to a folder.

    Args:
        db (Session): The database session.
        user_id (UUID): The ID of the user deleting the permission.
        permission_id (UUID): The ID of the permission to delete.

    Returns:
        A tuple containing a success boolean and an error code, or (False, error_code)
        if an error occurred.
    """

    permission = (
        db.query(FolderPermission).filter(FolderPermission.id == permission_id).first()
    )
    if not permission:
        return False, "NOT_FOUND"

    # Check if the user is the owner of the folder or the user the permission belongs to
    is_folder_owner = (
        db.query(FolderPermission)
        .filter(
            FolderPermission.folder_id == permission.folder_id,
            FolderPermission.user_id == user_id,
            FolderPermission.role == RoleEnum.owner,
        )
        .first()
    )

    if not is_folder_owner and permission.user_id != user_id:
        return False, "FORBIDDEN"

    try:
        db.delete(permission)
        db.commit()
        return True, None
    except SQLAlchemyError:
        db.rollback()
        return False, "INTERNAL_ERROR"


def create_file_permission(db: Session, user_id: UUID, data: CreateFilePermission):
    """
    Creates a new permission for a user to a file.

    Args:
        db (Session): The database session.
        user_id (UUID): The ID of the user creating the permission.
        data (CreateFilePermission): The permission data.

    Returns:
        A tuple containing the new permission and an error code, or (None, error_code)
        if an error occurred.
    """

    # Check if the user has owner permission to the specified file
    owner_permission = (
        db.query(FilePermission)
        .filter(
            FilePermission.file_id == data.id,
            FilePermission.user_id == user_id,
            FilePermission.role == RoleEnum.owner,
        )
        .first()
    )

    if not owner_permission:
        return None, "FORBIDDEN"

    # Get the target user
    target_user = get_user_by_email(db, data.email)
    if not target_user:
        return None, "NOT_FOUND"

    # Create the new permission
    new_permission = FilePermission(
        user_id=target_user.id,
        file_id=data.id,
        role=data.role.value,
    )

    try:
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
        return new_permission, None
    except IntegrityError:
        db.rollback()
        return None, "INTEGRITY_ERROR"
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"


def update_file_permission(db: Session, user_id: UUID, data: UpdateFilePermission):
    """
    Updates a permission for a user to a file.

    Args:
        db (Session): The database session.
        user_id (UUID): The ID of the user updating the permission.
        data (UpdateFilePermission): The permission data.

    Returns:
        A tuple containing the updated permission and an error code, or (None, error_code)
        if an error occurred.
    """

    # Check if the user has owner permission to the specified file
    owner_permission = (
        db.query(FilePermission)
        .filter(
            FilePermission.file_id == data.id,
            FilePermission.user_id == user_id,
            FilePermission.role == RoleEnum.owner,
        )
        .first()
    )

    if not owner_permission:
        return None, "FORBIDDEN"

    permission = db.query(FilePermission).filter(FilePermission.id == data.permission_id).first()
    if not permission:
        return None, "NOT_FOUND"

    permission.role = data.role.value

    try:
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission, None
    except SQLAlchemyError:
        db.rollback()
        return None, "INTERNAL_ERROR"


def delete_file_permission(db: Session, user_id: UUID, permission_id: UUID):
    """
    Deletes a permission for a user to a file.

    Args:
        db (Session): The database session.
        user_id (UUID): The ID of the user deleting the permission.
        permission_id (UUID): The ID of the permission to delete.

    Returns:
        A tuple containing a success boolean and an error code, or (False, error_code)
        if an error occurred.
    """

    permission = db.query(FilePermission).filter(FilePermission.id == permission_id).first()
    if not permission:
        return False, "NOT_FOUND"

    # Check if the user is the owner of the file or the user the permission belongs to
    is_file_owner = (
        db.query(FilePermission)
        .filter(
            FilePermission.file_id == permission.file_id,
            FilePermission.user_id == user_id,
            FilePermission.role == RoleEnum.owner,
        )
        .first()
    )

    if not is_file_owner and permission.user_id != user_id:
        return False, "FORBIDDEN"

    try:
        db.delete(permission)
        db.commit()
        return True, None
    except SQLAlchemyError:
        db.rollback()
        return False, "INTERNAL_ERROR"


def get_file_permission_by_id(db: Session, user_id: UUID, permission_id: UUID):
    try:
        permission = (
            db.query(FilePermission)
            .options(
                joinedload(FilePermission.file), joinedload(FilePermission.user)
            )
            .filter(
                FilePermission.id == permission_id,
                FilePermission.user_id == user_id,
            )
            .one_or_none()
        )
        if not permission:
            raise SQLAlchemyError
        return permission
    except SQLAlchemyError:
        return None


def get_file_permissions_by_file_id(db: Session, user_id: UUID, file_id: UUID):
    try:
        permissions = (
            db.query(FilePermission)
            .options(
                joinedload(FilePermission.file), joinedload(FilePermission.user)
            )
            .filter(
                FilePermission.file_id == file_id,
                FilePermission.user_id == user_id,
            )
            .all()
        )
        return permissions
    except SQLAlchemyError:
        return None


def get_all_file_permissions(db: Session, user_id: UUID):
    try:
        permissions = (
            db.query(FilePermission)
            .options(
                joinedload(FilePermission.file), joinedload(FilePermission.user)
            )
            .filter(FilePermission.user_id == user_id)
            .all()
        )
        return permissions
    except SQLAlchemyError:
        return None


def get_folder_permission_by_id(db: Session, user_id: UUID, permission_id: UUID):
    try:
        permission = (
            db.query(FolderPermission)
            .options(
                joinedload(FolderPermission.folder),
                joinedload(FolderPermission.user),
            )
            .filter(
                FolderPermission.id == permission_id,
                FolderPermission.user_id == user_id,
            )
            .one_or_none()
        )
        if not permission:
            raise SQLAlchemyError
        return permission
    except SQLAlchemyError:
        return None


def get_folder_permissions_by_folder_id(db: Session, user_id: UUID, folder_id: UUID):
    try:
        permissions = (
            db.query(FolderPermission)
            .options(
                joinedload(FolderPermission.folder),
                joinedload(FolderPermission.user),
            )
            .filter(
                FolderPermission.folder_id == folder_id,
                FolderPermission.user_id == user_id,
            )
            .all()
        )
        return permissions
    except SQLAlchemyError:
        return None


def get_all_folder_permissions(db: Session, user_id: UUID):
    try:
        permissions = (
            db.query(FolderPermission)
            .options(
                joinedload(FolderPermission.folder),
                joinedload(FolderPermission.user),
            )
            .filter(FolderPermission.user_id == user_id)
            .all()
        )
        return permissions
    except SQLAlchemyError:
        return None


