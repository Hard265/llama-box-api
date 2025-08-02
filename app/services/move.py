from typing import List
from sqlalchemy.orm import Session
from app.models.folder import Folder
from app.models.file import File
from app.models.user import User


def _is_subfolder(source_folder: Folder, destination_folder: Folder) -> bool:
    """Check if the destination folder is a subfolder of the source folder."""
    parent = destination_folder.parent
    while parent:
        if parent.id == source_folder.id:
            return True
        parent = parent.parent
    return False


def move_folders(
    session: Session,
    source_folders: List[Folder],
    destination_folder: Folder,
    user: User,
) -> List[Folder]:
    """Move a list of folders to a new destination."""
    moved_folders = []
    for folder in source_folders:
        if _is_subfolder(folder, destination_folder):
            raise ValueError("Cannot move a folder into its own subfolder.")
        folder.parent_id = destination_folder.id
        moved_folders.append(folder)
    return moved_folders


def move_files(
    session: Session, source_files: List[File], destination_folder: Folder, user: User
) -> List[File]:
    """Move a list of files to a new destination."""
    moved_files = []
    for file in source_files:
        file.folder_id = destination_folder.id
        moved_files.append(file)
    return moved_files
