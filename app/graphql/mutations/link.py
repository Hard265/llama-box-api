from uuid import uuid4, UUID
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
from app.graphql.errors import LinkOperationError
from app.services.link import create_link


@strawberry.type
class LinkMutations:
    @strawberry.mutation
    def create(self, info: Info, input: LinkInput) -> LinkType:
        user = info.context.get("user")
        if not user:
            raise LinkOperationError("Authentication required", "UNAUTHENTICATED")

        try:
            data = LinkCreate(**input.__dict__)
        except ValidationError as e:
            raise LinkOperationError("Invalid input data", "BAD_INPUT") from e

        db = next(get_db())
        try:
            link, error = create_link(db=db, data=data, user_id=UUID(user.sub))
            if error:
                if error == "NOT_FOUND":
                    raise LinkOperationError(
                        "Target not found or permission denied", "NOT_FOUND"
                    )
                if error == "BAD_INPUT":
                    raise LinkOperationError("Invalid input data", "BAD_INPUT")
            if not link:
                raise LinkOperationError("Failed to create link", "INTERNAL_ERROR")
            return link
        except SQLAlchemyError:
            db.rollback()
            raise LinkOperationError("Internal server error", "INTERNAL_ERROR")
