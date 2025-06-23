from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from app.database import get_db
from app.models.link import Link
from app.graphql.types import LinkType
from app.graphql.errors import LinkOperationError
from app.services.link import get_user_link, get_user_links, get_link


@strawberry.type
class LinkQueries:
    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[LinkType]:
        user = info.context.get("user")
        if not user:
            raise LinkOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        try:
            links = get_user_links(db=db, user_id=UUID(user.sub))
            return links
        except SQLAlchemyError as exc:
            raise LinkOperationError("Internal sever error", "INTERNAL_ERROR") from exc

    @strawberry.field
    def get(self, info: strawberry.Info, id: str) -> Optional[LinkType]:
        user = info.context.get("user")
        if not user:
            raise LinkOperationError("Authentication required", "UNAUTHENTICATED")

        try:
            link_id = UUID(id)
        except ValueError as exc:
            raise LinkOperationError("Invalid Link id format", "BAD_INPUT") from exc

        db = next(get_db())
        try:
            link = get_user_link(db=db, user_id=UUID(user.id), id=link_id)
            if not link:
                raise LinkOperationError("Link does not exist", "NOT_FOUND")

            return link
        except SQLAlchemyError:
            raise LinkOperationError("Internal sever error", "INTERNAL_ERROR")

    @strawberry.field
    def get_by_token(
        self, info: strawberry.Info, token: str, password: Optional[str] = None
    ) -> LinkType:
        """
        Get a link by its token, optionally checking for a password.
        """
        user = info.context.get("user")
        if not user:
            raise LinkOperationError("Authentication required", "UNAUTHENTICATED")

        db = next(get_db())
        try:
            link = get_link(db=db, token=token)
            if not link:
                raise LinkOperationError("Link does not exist", "NOT_FOUND")

            if link.password is not None and not link.check_password(password or ""):
                raise LinkOperationError(
                    "This link requires a valid password", "BAD_INPUT"
                )

            return link
        except SQLAlchemyError:
            raise LinkOperationError("Internal sever error", "INTERNAL_ERROR")
