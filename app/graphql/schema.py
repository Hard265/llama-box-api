import strawberry
from strawberry.fastapi import GraphQLRouter

from app.core.context import get_context
from app.graphql.mutations.file import FileMutations
from app.graphql.mutations.folder import FolderMutations
from app.graphql.mutations.link import LinkMutations
from app.graphql.queries.file import FileQueries
from app.graphql.queries.folder import FolderQueries
from app.graphql.queries.link import LinkQueries
from app.graphql.queries.permission import FilePermissionQueries, FolderPermissionQueries


@strawberry.type
class Query:
    @strawberry.field
    def link(self) -> LinkQueries:
        return LinkQueries()

    @strawberry.field
    def file(self) -> FileQueries:
        return FileQueries()

    @strawberry.field
    def folder(self) -> FolderQueries:
        return FolderQueries()

    @strawberry.field
    def file_permission(self) -> FilePermissionQueries:
        return FilePermissionQueries()

    @strawberry.field
    def folder_permission(self) -> FolderPermissionQueries:
        return FolderPermissionQueries()


@strawberry.type
class Mutation:
    @strawberry.field
    def link(self) -> LinkMutations:
        return LinkMutations()

    @strawberry.field
    def folder(self) -> FolderMutations:
        return FolderMutations()

    @strawberry.field
    def file(self) -> FileMutations:
        return FileMutations()


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(
    schema, multipart_uploads_enabled=True, context_getter=get_context
)