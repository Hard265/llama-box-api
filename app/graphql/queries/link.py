from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
import strawberry
from strawberry.exceptions import StrawberryGraphQLError
from app.database import get_db
from app.graphql.types import LinkType
from app.services.link import (
    get_user_link,
    get_user_links,
    get_link,
    get_links_by_file_id,
    get_links_by_folder_id,
)


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
    def get(self, info: strawberry.Info, id: UUID) -> Optional[LinkType]:
        user = info.context.get("user")

        db = next(get_db())
        try:
            link = get_user_link(db=db, user_id=UUID(user.sub), id=id)
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

    @strawberry.field
    def get_by_file(self, info: strawberry.Info, file_id: UUID) -> Sequence[LinkType]:
        user = info.context.get("user")
        db = next(get_db())
        try:
            links, error = get_links_by_file_id(
                db=db, user_id=UUID(user.sub), file_id=file_id
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not retrieve links", extensions={"code": error}
                )
            if not links:
                raise StrawberryGraphQLError(
                    message="Could not retrieve links",
                    extensions={"code": "INTERNAL_ERROR"},
                )
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
    def get_by_folder(
        self, info: strawberry.Info, folder_id: UUID
    ) -> Sequence[LinkType]:
        user = info.context.get("user")

        db = next(get_db())
        try:
            links, error = get_links_by_folder_id(
                db=db, user_id=UUID(user.sub), folder_id=folder_id
            )
            if error:
                raise StrawberryGraphQLError(
                    message="Could not retrieve links", extensions={"code": error}
                )
            if not links:
                raise StrawberryGraphQLError(
                    message="Could not retrieve links",
                    extensions={"code": "INTERNAL_ERROR"},
                )

            return links
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Database error occurred while retrieving links",
                extensions={"code": "INTERNAL_ERROR"},
            )
        finally:
            db.close()
