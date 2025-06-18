import enum
from uuid import uuid4
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    UUID,
    UniqueConstraint,
    Enum as SQLAEnum,
)
from sqlalchemy.orm import relationship
from app.database import Base


class RoleEnum(str, enum.Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class FilePermission(Base):
    __tablename__ = "file_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_sub = Column(String, nullable=False)
    file_id = Column(ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLAEnum(RoleEnum), nullable=False)
    __table_args__ = (
        UniqueConstraint("user_sub", "role", "file_id", name="uq_user_resource_role"),
    )
    file = relationship("File", back_populates="permissions")


class FolderPermission(Base):
    __tablename__ = "folder_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_sub = Column(String, nullable=False)
    folder_id = Column(ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLAEnum(RoleEnum), nullable=False)
    __table_args__ = (
        UniqueConstraint("user_sub", "folder_id", "role", name="uq_user_resource_role"),
    )

    folder = relationship("Folder", back_populates="permissions")
