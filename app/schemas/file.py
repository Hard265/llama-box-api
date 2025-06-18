from pydantic import BaseModel, constr
from uuid import UUID
from typing import Optional

class CreateFile(BaseModel):
    name: Optional[str]
    folder_id: UUID
    file: str
    
class UpdateFile(BaseModel):
    name: str
