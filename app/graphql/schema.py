import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.queries.link import LinkQueries
from app.graphql.queries.file import FileQueries
from app.graphql.queries.folder import FolderQueries

from app.graphql.mutations.link import LinkMutations
from app.graphql.mutations.folder import FolderMutations
from app.graphql.mutations.file import FileMutations


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
graphql_app = GraphQLRouter(schema, multipart_uploads_enabled=True)
