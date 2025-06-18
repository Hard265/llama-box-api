from uuid import uuid4
from sqlalchemy import Column, String, Boolean, UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    password = Column(String, nullable=False)
    file_permissions = relationship(
        "FilePermission", back_populates="user", cascade="all, delete-orphan"
    )
    folder_permissions = relationship(
        "FolderPermission", back_populates="user", cascade="all, delete-orphan"
    )
