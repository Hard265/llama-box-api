from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.services.file import get_user_file, generate_thumbnail
from app.schemas.auth import TokenData
from app.core.auth import get_current_user
from app.database import get_db
from uuid import UUID

router = APIRouter()


@router.get("/{id}")
async def get_file(
    id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.sub
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    file, error = get_user_file(
        db, UUID(user_id) if isinstance(user_id, str) else user_id, id
    )
    if error == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="File not found")
    if error:
        raise HTTPException(status_code=500, detail=error)
    return FileResponse(file.file, media_type=file.mime_type, filename=file.name)


@router.get("/t/{id}")
async def get_thumbnail(
    id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.sub
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    file, error = get_user_file(
        db, UUID(user_id) if isinstance(user_id, str) else user_id, id
    )
    if error == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="File not found")
    if error:
        raise HTTPException(status_code=500, detail=error)

    if not file.mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")

    thumbnail_io, error = generate_thumbnail(file.file)
    if error:
        raise HTTPException(
            status_code=500, detail=f"Thumbnail generation failed: {error}"
        )

    return StreamingResponse(thumbnail_io, media_type="image/png")
