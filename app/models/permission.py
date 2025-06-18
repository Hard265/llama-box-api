import enum
from uuid import uuid4
from sqlalchemy import (
    Column,
    ForeignKey,
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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),  nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLAEnum(RoleEnum), nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "role", "file_id", name="uq_user_resource_role"),
    )
    file = relationship("File", back_populates="permissions")
    user = relationship("User", back_populates="file_permissions", foreign_keys=[user_id])


class FolderPermission(Base):
    __tablename__ = "folder_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    folder_id = Column(UUID(as_uuid=True),ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLAEnum(RoleEnum), nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "folder_id", "role", name="uq_user_resource_role"),
    )

    folder = relationship("Folder", back_populates="permissions")
    user = relationship("User", back_populates="folder_permissions", foreign_keys=[user_id])
