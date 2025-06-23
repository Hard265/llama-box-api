from graphql import GraphQLError


class FileOperationError(GraphQLError):
    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")

class FolderOperationError(FileOperationError):
    pass

class LinkOperationError(FileOperati
    pass
