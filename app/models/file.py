from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    UUID,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from typing import Optional
from app.models.permission import RoleEnum
from app.models.user import User


class File(Base):
    __tablename__ = "files"
    __table_args__ = (UniqueConstraint("name", "folder_id", name="uq_name_parent"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    file = Column(String, nullable=False)
    name = Column(String(255), nullable=False)
    mime_type = Column(String(55), nullable=False)
    ext = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False, default=0)
    starred = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    folder = relationship(
        "Folder",
        back_populates="files",
    )
    links = relationship(
        "Link", back_populates="file", cascade="all, delete", passive_deletes=True
    )
    permissions = relationship(
        "FilePermission", back_populates="file", cascade="all, delete-orphan"
    )

    @property
    def owner(self) -> Optional[User]:
        return next(
            (perm.user for perm in self.permissions if perm.role == RoleEnum.viewer),
            None,
        )

    @property
    def is_shared(self) -> bool:
        return len(self.permissions) > 1 or len(self.links) > 0
