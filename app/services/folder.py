from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.models.permission import FolderPermission, RoleEnum
from app.schemas.folders import FolderCreate


def create_folder_with_owner(
    db: Session, folder_data: FolderCreate, user_id: UUID
) -> Folder:
    if folder_data.parent_id:
        parent = db.query(Folder).filter(Folder.id == folder_data.parent_id).first()
        if not parent:
            raise ValueError(
                f"Parent folder with ID {folder_data.parent_id} does not exist"
            )

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
        return folder
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            "Folder creation failed: likely duplicate name or invalid parent"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Database error occurred") from e
    finally:
        db.close()
