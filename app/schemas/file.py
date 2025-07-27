from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class CreateFile(BaseModel):
    name: Optional[str]
    folder_id: Optional[UUID] = None
    file: str
    mime_type: str
    ext: str
    size: int
    
class UpdateFile(BaseModel):
    name: str  

from datetime import datetime

class FileOut(BaseModel):
    id: UUID
    name: Optional[str]
    folder_id: Optional[UUID]
    file: str
    mime_type: str
    ext: str
    size: int
    starred: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

FileOut.model_rebuild()
