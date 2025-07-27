import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.file_uploads import Upload

from app.core.context import get_context
from app.graphql.mutations.file import FileMutations
from app.graphql.mutations.folder import FolderMutations
from app.graphql.mutations.link import LinkMutations
from app.graphql.mutations.permission import FilePermissionMutations, FolderPermissionMutations
from app.graphql.queries.file import FileQueries
from app.graphql.queries.folder import FolderQueries
from app.graphql.queries.link import LinkQueries
from app.graphql.queries.permission import (
    FilePermissionQueries,
    FolderPermissionQueries,
)
from app.graphql.permissions import IsAuthenticated


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    def link(self) -> LinkQueries:
        return LinkQueries()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def file(self) -> FileQueries:
        return FileQueries()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def folder(self) -> FolderQueries:
        return FolderQueries()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def file_permission(self) -> FilePermissionQueries:
        return FilePermissionQueries()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def folder_permission(self) -> FolderPermissionQueries:
        return FolderPermissionQueries()


@strawberry.type
class Mutation:
    @strawberry.field(permission_classes=[IsAuthenticated])
    def link(self) -> LinkMutations:
        return LinkMutations()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def folder(self) -> FolderMutations:
        return FolderMutations()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def file(self) -> FileMutations:
        return FileMutations()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def file_permission(self) -> FilePermissionMutations:
        return FilePermissionMutations()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def folder_permission(self) -> FolderPermissionMutations:
        return FolderPermissionMutations()


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
graphql_app = GraphQLRouter(
    schema, multipart_uploads_enabled=True, context_getter=get_context
)
