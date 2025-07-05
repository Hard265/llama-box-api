from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class CreateFile(BaseModel):
    name: Optional[str]
    folder_id: UUID
    file: str
    
class UpdateFile(BaseModel):
    name: str

class FileOut(BaseModel):
    id: UUID
    name: str
    folder_id: UUID
    size: int
    mime_type: Optional[str] = None  # e.g., "image/png"
    created_at: str  # ISO format string
    updated_at: str  # ISO format string

    model_config = ConfigDict(from_attributes=True)  
