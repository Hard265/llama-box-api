import enum
from datetime import datetime
from pydantic import BaseModel, UUID4, model_validator
from typing import Optional


class LinkPermission(str, enum.Enum):
    edit = "edit"
    view = "view"


class LinkCreate(BaseModel):
    file_id: Optional[UUID4] = None
    folder_id: Optional[UUID4] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    permission: Optional[LinkPermission] = LinkPermission.view

    @model_validator(mode="before")
    @classmethod
    def validate_target(cls, values):
        file_id, folder_id = values.get("file_id"), values.get("folder_id")
        if not file_id and not folder_id:
            raise ValueError("Either file_id or folder_id must be provided")
        if file_id and folder_id:
            raise ValueError("Only one of file_id or folder_id must be provided")
        return values


class LinkOut(BaseModel):
    id: UUID4
    token: str
    created_at: datetime
    expires_at: Optional[datetime]
    permission: LinkPermission

    class Config:
        model_attributes = True
