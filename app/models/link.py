from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import UUID, Column, ForeignKey,String, DateTime
from sqlalchemy.orm import relationship, validates
from secrets import token_urlsafe

from app.database import Base
from app.utils.security import hash_password, verify_password

class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    token = Column(
        String(48), 
        unique=True, 
        default=lambda: token_urlsafe(32), 
        nullable=False, 
        index=True
    )

    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=True)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    shared_with_sub = Column(String, nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    file = relationship("File", back_populates="links")
    folder = relationship("Folder", back_populates="links")

    @validates("password")
    def _hash_password(self, key, value):
        return hash_password(value) if value else None

    def check_password(self, password: str) -> bool:
        return self.password and verify_password(password, self.password)

    @property
    def target_type(self):
        return "file" if self.file_id else "folder"

    @property
    def target_id(self):
        return self.file_id or self.folder_id

    @property
    def is_public(self):
        return True if not self.shared_with_sub else False
