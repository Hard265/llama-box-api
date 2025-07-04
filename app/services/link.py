from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.schemas.link import LinkCreate
from app.models.link import Link
from app.models.file import File
from app.models.folder import Folder
from app.models.permission import FilePermission, RoleEnum, FolderPermission
from datetime import datetime, timezone


def get_user_link(db: Session, user_id: UUID, id: UUID):
    link = (
        db.query(Link)
        .options(joinedload(Link.user), joinedload(Link.folder), joinedload(Link.file))
        .filter(Link.user_id == user_id, Link.id == id)
        .first()
    )
    return link


def get_user_links(db: Session, user_id: UUID):
    links = (
        db.query(Link)
        .options(joinedload(Link.user), joinedload(Link.folder), joinedload(Link.file))
        .filter(Link.user_id == user_id)
        .all()
    )
    return links


def get_link(db: Session, token: str):
    link = db.query(Link).filter(Link.token == token).first()
    return link


def get_links_by_file_id(db: Session, user_id: UUID, file_id: UUID):
    # Check if the user has permission to access the file
    file_permission = (
        db.query(FilePermission)
        .filter(
            FilePermission.file_id == file_id,
            FilePermission.user_id == user_id,
        )
        .first()
    )
    if not file_permission:
        return None, "PERMISSION_DENIED"

    links = (
        db.query(Link)
        .options(joinedload(Link.user), joinedload(Link.folder), joinedload(Link.file))
        .filter(Link.file_id == file_id)
        .all()
    )
    return links, None


def get_links_by_folder_id(db: Session, user_id: UUID, folder_id: UUID):
    # Check if the user has permission to access the folder
    folder_permission = (
        db.query(FolderPermission)
        .filter(
            FolderPermission.folder_id == folder_id,
            FolderPermission.user_id == user_id,
        )
        .first()
    )
    if not folder_permission:
        return None, "PERMISSION_DENIED"

    links = (
        db.query(Link)
        .options(joinedload(Link.user), joinedload(Link.folder), joinedload(Link.file))
        .filter(Link.folder_id == folder_id)
        .all()
    )
    return links, None


def create_link(db: Session, data: LinkCreate, user_id: UUID):
    if data.file_id:
        target = (
            db.query(File)
            .join(FilePermission)
            .filter(
                File.id == data.file_id,
                FilePermission.user_id == user_id,
                FilePermission.role == RoleEnum.owner,
            )
            .first()
        )
        if not target:
            return None, "NOT_FOUND"
    elif data.folder_id:
        target = (
            db.query(Folder)
            .join(FolderPermission)
            .filter(
                Folder.id == data.folder_id,
                FolderPermission.user_id == user_id,
                FolderPermission.role == RoleEnum.owner,
            )
            .first()
        )
        if not target:
            return None, "NOT_FOUND"
    else:
        return None, "BAD_INPUT"

    link = Link(
        file_id=data.file_id,
        folder_id=data.folder_id,
        password=data.password,
        user_id=user_id,
        permisssion=data.permission,
        expires_at=data.expires_at,
        created_at=datetime.now(timezone.utc),
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link, None
