from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.link import Link
from app.schemas.file import FileOut
from app.schemas.folder import FolderOut

# /s routes for shared links
router = APIRouter()


@router.get("/{token}")
async def read_share(
    token: str, password: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    Retrieve a share by its token.
    """
    link = db.query(Link).filter(Link.token == token).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found",
        )

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share has expired",
        )

    if link.password and not link.check_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid password required to access this share",
        )

    target = link.file or link.folder
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found for this share",
        )

    return (
        FileOut.model_validate(target)
        if link.file
        else FolderOut.model_validate(target)
    )
