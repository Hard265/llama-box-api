from datetime import datetime, timezone
from typing import Optional
from typing import List
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.database import Base
from app.models.permission import RoleEnum
from app.models.user import User


class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (
        # Ensures a folder's name is unique within its parent.
        UniqueConstraint("name", "parent_id", name="uq_folder_name_parent"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)

    # Self-referential foreign key. This is the core of the hierarchy.
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "folders.id",
            # Tells the DATABASE to cascade deletes. When a folder is deleted,
            # the DB will automatically delete children folders.
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    starred = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---

    # Relationship to child files. `cascade="all, delete"` ensures that when a Folder
    # is deleted, all its associated File objects are also deleted by the ORM.
    files = relationship("File", back_populates="folder", cascade="all, delete")

    # Relationship to child links.
    links = relationship("Link", back_populates="folder", cascade="all, delete")

    # Relationship to permissions. `delete-orphan` means if a permission is
    # removed from this list, it's deleted from the DB entirely.
    permissions = relationship(
        "FolderPermission", back_populates="folder", cascade="all, delete-orphan"
    )

    # The self-referential relationship to children folders.
    folders = relationship(
        "Folder",
        # `cascade="all, delete-orphan"` tells the ORM to manage children. If a
        # child is removed from this list, it's deleted. If the parent is
        # deleted, all children in this list are deleted.
        cascade="all, delete-orphan",
        # `backref` creates the `.parent` attribute on the child object.
        # `remote_side` is crucial for self-referential relationships.
        backref=backref("parent", remote_side=[id]),
        # `passive_deletes=True` tells the ORM to NOT issue its own DELETE
        # statements for the children, and instead trust the `ondelete="CASCADE"`
        # we configured on the ForeignKey. This is much more efficient.
        passive_deletes=True,
    )

    @property
    def owner(self) -> Optional["User"]:
        """Convenience property to get the folder's owner."""
        return next(
            (perm.user for perm in self.permissions if perm.role == RoleEnum.owner),
            None,
        )

    @property
    def path(self) -> List[dict]:
        """Builds the breadcrumb path from the root to the current folder."""
        parts = []
        current = self
        while current is not None:
            parts.append({"id": current.id, "name": current.name})
            current = current.parent

        # The root of the filesystem doesn't exist in the DB, so we add it virtually.
        root = [{"id": None, "name": "Root"}]
        return root + list(reversed(parts))

    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
