from uuid import UUID
from pydantic import ValidationError
import strawberry
from strawberry import Info
from sqlalchemy.exc import SQLAlchemyError
from strawberry.exceptions import StrawberryGraphQLError

from app.database import get_db
from app.graphql.types import LinkInput, LinkType
from app.schemas.link import LinkCreate
from app.services.link import create_link


@strawberry.type
class LinkMutations:
    @strawberry.mutation
    def create(self, info: Info, input: LinkInput) -> LinkType:
        user = info.context.get("user")
        try:
            data = LinkCreate(**input.__dict__)
        except ValidationError as e:
            raise StrawberryGraphQLError(
                "Invalid input data", extensions={"code": "BAD_INPUT"}
            ) from e

        db = next(get_db())
        try:
            link, error = create_link(db=db, data=data, user_id=UUID(user.sub))
            if error:
                raise StrawberryGraphQLError(
                    message="Could not create link", extensions={"code": error}
                )
            return link
        except SQLAlchemyError:
            db.rollback()
            raise StrawberryGraphQLError(
                "Internal server error", extensions={"code": "INTERNAL_ERROR"}
            )
        finally:
            db.close()
