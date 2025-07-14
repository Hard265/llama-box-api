import os
from sqlalchemy import select, literal
from sqlalchemy.orm import Session, aliased
from uuid import UUID
from app.models.folder import Folder

def get_folder_path_cte(session: Session, folder_id: UUID):
    folders = Folder.__table__

    # Anchor: current folder
    base = select(
        folders.c.id,
        folders.c.name,
        folders.c.parent_id,
        literal(0).label("level")
    ).where(folders.c.id == folder_id)

    # Define CTE first
    path_cte = base.cte(name="path_cte", recursive=True)

    # Alias for folders and CTE to prevent name collisions
    folders_alias = aliased(folders)
    path_alias = aliased(path_cte)

    # Recursive term: join folders to CTE
    recursive = select(
        folders_alias.c.id,
        folders_alias.c.name,
        folders_alias.c.parent_id,
        (path_alias.c.level + 1).label("level")
    ).join(
        path_alias,
        folders_alias.c.id == path_alias.c.parent_id
    )

    # Final recursive CTE
    path_cte = path_cte.union_all(recursive)

    # Final query
    stmt = select(path_cte.c.id, path_cte.c.name).order_by(path_cte.c.level.desc())
    return session.execute(stmt).all()

MEDIA_ROOT = "media"
os.makedirs(MEDIA_ROOT, exist_ok=True)
