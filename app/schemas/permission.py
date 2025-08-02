from uuid import UUID
from enum import Enum
from pydantic import BaseModel, EmailStr


class Role(Enum):
    editor = "editor"
    viewer = "viewer"


class CreateFolderPermission(BaseModel):
    id: UUID
    email: EmailStr
    role: Role


class UpdateFolderPermission(BaseModel):
    permission_id: UUID
    role: Role


class CreateFilePermission(BaseModel):
    id: UUID
    email: EmailStr
    role: Role


class UpdateFilePermission(BaseModel):
    id: UUID
    permission_id: UUID
    role: Role
