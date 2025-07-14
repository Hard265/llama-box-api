from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.folder import Folder
from app.models.file import File
from app.models.user import User
from app.models.permission import FolderPermission, FilePermission, RoleEnum


class CopyService:
    """Service class for handling folder and file copy operations."""

    def __init__(self, session: Session):
        self.session = session

    def copy_folder(
        self,
        source_folder: Folder,
        destination_parent: Optional[Folder] = None,
        new_name: Optional[str] = None,
        user: Optional[User] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Folder:
        """
        Copy a folder with advanced options.
        
        Args:
            source_folder: The folder to copy
            destination_parent: Parent folder for the copy
            new_name: Name for the copied folder
            user: User performing the copy (for permission checks)
            options: Additional copy options
            
        Returns:
            The newly created folder copy
        """
        options = options or {}

        # Validate permissions
        if user and not self._can_copy_folder(source_folder, user):
            raise PermissionError("User does not have permission to copy this folder")

        # Check destination permissions
        if destination_parent and user and not self._can_create_in_folder(destination_parent, user):
            raise PermissionError(
                "User does not have permission to create in destination folder"
            )

        # Perform the copy
        return self._perform_folder_copy(
            source_folder=source_folder,
            destination_parent=destination_parent,
            new_name=new_name,
            user=user,
            **options,
        )

    def _perform_folder_copy(
        self,
        source_folder: Folder,
        destination_parent: Optional[Folder],
        new_name: Optional[str],
        user: Optional[User],
        copy_permissions: bool = True,
        copy_children: bool = True,
        preserve_timestamps: bool = False,
        **kwargs,
    ) -> Folder:
        """Internal method to perform the actual folder copy."""

        # Generate name
        if new_name is None:
            new_name = self._generate_unique_folder_name(
                source_folder.name, destination_parent, suffix=" (Copy)"
            )

        # Create the folder copy
        folder_copy = Folder(
            name=new_name,
            parent_id=destination_parent.id if destination_parent else None,
            starred=source_folder.starred,
        )

        # Preserve timestamps if requested
        if preserve_timestamps:
            folder_copy.created_at = source_folder.created_at
            folder_copy.updated_at = source_folder.updated_at

        self.session.add(folder_copy)
        self.session.flush()

        # Copy permissions
        if copy_permissions:
            self._copy_folder_permissions(source_folder, folder_copy, user)

        # Copy children
        if copy_children:
            self._copy_folder_children(source_folder, folder_copy, user)

        return folder_copy

    def _copy_folder_permissions(
        self, source: Folder, target: Folder, user: Optional[User]
    ) -> None:
        """Copy folder permissions with user context."""
        for perm in source.permissions:
            # Skip if user doesn't have permission to grant this role
            if user and not self._can_grant_permission(user, perm.role):
                continue

            new_perm = FolderPermission(
                folder_id=target.id, user_id=perm.user_id, role=perm.role
            )
            self.session.add(new_perm)
        self.session.flush()

    def _copy_folder_children(
        self, source: Folder, target: Folder, user: Optional[User]
    ) -> None:
        """Copy all children of a folder recursively."""
        # Copy subfolders
        for subfolder in source.folders:
            self._perform_folder_copy(
                source_folder=subfolder,
                destination_parent=target,
                new_name=subfolder.name,
                user=user,
                copy_permissions=True,
                copy_children=True,
            )

        # Copy files
        for file in source.files:
            self.copy_file(file, target, user=user)

    def copy_file(
        self,
        source_file: File,
        destination_folder: Folder,
        new_name: Optional[str] = None,
        user: Optional[User] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> File:
        """
        Copy a file with advanced options.
        
        Args:
            source_file: The file to copy
            destination_folder: Folder for the copy
            new_name: Name for the copied file
            user: User performing the copy (for permission checks)
            options: Additional copy options
            
        Returns:
            The newly created file copy
        """
        options = options or {}

        # Validate permissions
        if user and not self._can_copy_file(source_file, user):
            raise PermissionError("User does not have permission to copy this file")

        # Check destination permissions
        if user and not self._can_create_in_folder(destination_folder, user):
            raise PermissionError(
                "User does not have permission to create in destination folder"
            )

        # Perform the copy
        return self._perform_file_copy(
            source_file=source_file,
            destination_folder=destination_folder,
            new_name=new_name,
            user=user,
            **options,
        )

    def _perform_file_copy(
        self,
        source_file: File,
        destination_folder: Folder,
        new_name: Optional[str],
        user: Optional[User],
        copy_permissions: bool = True,
        preserve_timestamps: bool = False,
        **kwargs,
    ) -> File:
        """Internal method to perform the actual file copy."""

        # Generate name
        if new_name is None:
            new_name = self._generate_unique_file_name(
                source_file.name, destination_folder, suffix=" (Copy)"
            )

        # Create the file copy
        file_copy = File(
            name=new_name,
            folder_id=destination_folder.id,
            file=source_file.file,  # This assumes the file path is the same
            mime_type=source_file.mime_type,
            ext=source_file.ext,
            size=source_file.size,
            starred=source_file.starred,
        )

        # Preserve timestamps if requested
        if preserve_timestamps:
            file_copy.created_at = source_file.created_at
            file_copy.updated_at = source_file.updated_at

        self.session.add(file_copy)
        self.session.flush()

        # Copy permissions
        if copy_permissions:
            self._copy_file_permissions(source_file, file_copy, user)

        return file_copy

    def _copy_file_permissions(
        self, source: File, target: File, user: Optional[User]
    ) -> None:
        """Copy file permissions with user context."""
        for perm in source.permissions:
            # Skip if user doesn't have permission to grant this role
            if user and not self._can_grant_permission(user, perm.role):
                continue

            new_perm = FilePermission(
                file_id=target.id, user_id=perm.user_id, role=perm.role
            )
            self.session.add(new_perm)

    def _generate_unique_folder_name(
        self, base_name: str, parent: Optional[Folder], suffix: str = " (Copy)"
    ) -> str:
        """Generate a unique name for the folder copy."""
        candidate_name = f"{base_name}{suffix}"
        counter = 1

        while self._folder_name_exists(candidate_name, parent):
            candidate_name = f"{base_name}{suffix} ({counter})"
            counter += 1

        return candidate_name

    def _folder_name_exists(self, name: str, parent: Optional[Folder]) -> bool:
        """Check if a folder name already exists in the parent folder."""
        query = self.session.query(Folder).filter(Folder.name == name)

        if parent:
            query = query.filter(Folder.parent_id == parent.id)
        else:
            query = query.filter(Folder.parent_id.is_(None))

        return query.first() is not None

    def _generate_unique_file_name(
        self, base_name: str, parent: Folder, suffix: str = " (Copy)"
    ) -> str:
        """Generate a unique name for the file copy."""
        candidate_name = f"{base_name}{suffix}"
        counter = 1

        while self._file_name_exists(candidate_name, parent):
            candidate_name = f"{base_name}{suffix} ({counter})"
            counter += 1

        return candidate_name

    def _file_name_exists(self, name: str, parent: Folder) -> bool:
        """Check if a file name already exists in the parent folder."""
        return (
            self.session.query(File)
            .filter(File.name == name, File.folder_id == parent.id)
            .first()
            is not None
        )

    def _can_copy_folder(self, folder: Folder, user: User) -> bool:
        """Check if user can copy this folder."""
        # Implementation depends on your permission system
        return True

    def _can_copy_file(self, file: File, user: User) -> bool:
        """Check if user can copy this file."""
        # Implementation depends on your permission system
        return True

    def _can_create_in_folder(self, folder: Folder, user: User) -> bool:
        """Check if user can create in this folder."""
        # Implementation depends on your permission system
        return True

    def _can_grant_permission(self, user: User, role: RoleEnum) -> bool:
        """Check if user can grant this permission role."""
        # Implementation depends on your permission system
        return True
