from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, List, Dict
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.permission import RoleEnum
from app.models.user import User


class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint("name", "parent_id", name="uq_folder_name_parent"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "folders.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=True,
    )

    starred = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    files = relationship("File", back_populates="folder", cascade="all, delete")
    links = relationship(
        "Link", back_populates="folder", cascade="all, delete", passive_deletes=True
    )
    permissions = relationship(
        "FolderPermission", back_populates="folder", cascade="all, delete-orphan"
    )
    parent = relationship("Folder", remote_side=[id], backref="folders")

    @property
    def owner(self) -> Optional[User]:
        return next(
            (perm.user for perm in self.permissions if perm.role == RoleEnum.owner),
            None,
        )

    @property
    def path(self):
        parts = []
        current = self
        while current is not None:
            parts.append({"id": current.id, "name": current.name})
            current = current.parent
        parts.reverse()
        parts = [{"id": None, "name": "Root"}] + parts
        return parts
