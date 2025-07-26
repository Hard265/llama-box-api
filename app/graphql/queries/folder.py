from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import strawberry
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.graphql.types import FolderType
from app.services.folder import get_folder, get_folders
from app.utils.helpers import get_folder_path_cte


@strawberry.type
class FolderQueries:
    @strawberry.field
    def get(self, info: strawberry.Info, id: UUID) -> Optional[FolderType]:
        user = info.context.get("user")
        db: Session = next(get_db())
        try:
            print(get_folder_path_cte(db, id))
            folder = get_folder(db=db, user_id=UUID(user.sub), id=id)
            if not folder:
                raise StrawberryGraphQLError(
                    message="Folder does not exist",
                    extensions={"code": "NOT_FOUND"},
                )
            return FolderType(
                id=folder.id,
                name=folder.name,
                created_at=folder.created_at,
                updated_at=folder.updated_at,
                folders=folder.folders,
                files=folder.files,
                links=folder.links,
                is_shared=folder.is_shared,
                permissions=folder.permissions,
                owner=folder.owner,
                path=get_folder_path_cte(db, id),
            )
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving folder",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def get_all(
        self, info: strawberry.Info, parent_id: Optional[UUID] = None
    ) -> Sequence[FolderType]:
        user = info.context.get("user")
        db = next(get_db())
        try:
            folders = list(
                get_folders(db=db, user_id=UUID(user.sub), parent_id=parent_id)
            )
            return folders
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                message="Database error occurred while retrieving folders",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
