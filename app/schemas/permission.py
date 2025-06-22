from uuid import UUID
from enum import Enum
from pydantic import BaseModel


class Role(Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class CreateFilePermission(BaseModel):
    user_id: UUID
    file_id: UUID
    role: Role
