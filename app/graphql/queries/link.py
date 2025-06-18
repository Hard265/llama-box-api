from re import U
from typing import Optional, Sequence
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
import strawberry
from app.database import get_db
from app.models.link import Link
from app.graphql.types import LinkType


@strawberry.type
class LinkQueries:
    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[LinkType]:
        db = next(get_db())

        try:
            links = db.query(Link).all()
            return links
        except SQLAlchemyError:
            raise Exception("Internal sever error")

    @strawberry.field
    def get(self, info: strawberry.Info, token: str, password: Optional[str] = None) -> Optional[LinkType]:
        db = next(get_db())
        try:
            link = db.query(Link).filter(Link.token==token).first()
            if not link:
                raise Exception("Link not found")

            if link.password is not None and not link.check_password(password or ""):
                raise Exception("This link requires a valid password")

            return link
        except SQLAlchemyError:
            raise Exception("Internal sever error")
