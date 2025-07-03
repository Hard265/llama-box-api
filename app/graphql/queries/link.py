from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.exceptions import StrawberryGraphQLError
from app.database import get_db
from app.graphql.types import LinkType
from app.services.link import get_user_link, get_user_links, get_link


@strawberry.type
class LinkQueries:
    @strawberry.field
    def get_all(self, info: strawberry.Info) -> Sequence[LinkType]:
        user = info.context.get("user")
        db = next(get_db())
        try:
            links = get_user_links(db=db, user_id=UUID(user.sub))
            return links
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while retrieving links",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def get(self, info: strawberry.Info, id: str) -> Optional[LinkType]:
        user = info.context.get("user")
        try:
            link_id = UUID(id)
        except ValueError as exc:
            raise StrawberryGraphQLError(
                message="Invalid Link id format", extensions={"code": "BAD_INPUT"}
            ) from exc

        db = next(get_db())
        try:
            link = get_user_link(db=db, user_id=UUID(user.sub), id=link_id)
            if not link:
                raise StrawberryGraphQLError(
                    message="Link does not exist", extensions={"code": "NOT_FOUND"}
                )

            return link
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while retrieving link",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()

    @strawberry.field
    def get_by_token(
        self, info: strawberry.Info, token: str, password: Optional[str] = None
    ) -> LinkType:
        """
        Get a link by its token, optionally checking for a password.
        """
        db = next(get_db())
        try:
            link = get_link(db=db, token=token)
            if not link:
                raise StrawberryGraphQLError(
                    message="Link does not exist", extensions={"code": "NOT_FOUND"}
                )

            if link.password is not None and not link.check_password(password or ""):
                raise StrawberryGraphQLError(
                    message="This link requires a valid password",
                    extensions={"code": "BAD_INPUT"},
                )

            return link
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while retrieving link by token",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
