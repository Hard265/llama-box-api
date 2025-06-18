from uuid import uuid4
from pydantic import ValidationError
import strawberry
from datetime import datetime, timezone
from strawberry import Info
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models.file import File
from app.models.folder import Folder
from app.models.link import Link
from app.graphql.types import LinkInput, LinkType
from app.schemas.link import LinkCreate

@strawberry.type
class LinkMutations:
    @strawberry.mutation
    def create(self, info: Info, input: LinkInput) -> LinkType:
        try:
            data = LinkCreate(**input.__dict__)
        except ValidationError as e:
            raise Exception(e.json())

        db = next(get_db())
        
        try:

            if data.file_id:
                target = db.query(File).get(data.file_id)
                if not target:
                    raise Exception("File not found")
            elif data.folder_id:
                target = db.query(Folder).get(data.folder_id)
                if not target:
                    raise Exception("Folder not found")
            else:
                raise Exception("Either file_id or folder_id must be provided")
            
            token = uuid4()
            link = Link(
                file_id=data.file_id,
                folder_id=data.folder_id,
                password=data.password,
                expires_at=data.expires_at,
                created_at=datetime.now(timezone.utc),
            )

            db.add(link)
            db.commit()
            db.refresh(link)

            return link
        except SQLAlchemyError:
            db.rollback()
            raise Exception("Intenal server error")
