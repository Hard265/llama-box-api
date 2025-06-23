from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class FolderBase(BaseModel):
    name: str = Field(..., max_length=255)
    parent_id: Optional[UUID] = None

class FolderCreate(FolderBase):
    pass

class FolderUpdate(BaseModel):
    id: UUID
    name: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[UUID] = None

class FolderOut(FolderBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    folders: List["FolderOut"] = []

    class Config:
        from_attributes = True

FolderOut.model_rebuild()

