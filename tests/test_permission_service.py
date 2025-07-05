"""
import uuid

import pytest
from sqlalchemy.orm import Session

from app.models.file import File
from app.models.folder import Folder
from app.models.permission import FilePermission, FolderPermission, RoleEnum
from app.models.user import User
from app.schemas.file import CreateFile
from app.schemas.folder import FolderCreate
from app.schemas.permission import (
    CreateFilePermission,
    CreateFolderPermission,
    UpdateFilePermission,
    UpdateFolderPermission,
)
from app.services import file as file_service
from app.services import folder as folder_service
from app.services import permission as permission_service


@pytest.fixture
def setup_users(db_session: Session):
    user1 = User(email="test1@example.com", password="password")
    user2 = User(email="test2@example.com", password="password")
    user3 = User(email="test3@example.com", password="password")
    db_session.add_all([user1, user2, user3])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    db_session.refresh(user3)
    return user1, user2, user3


@pytest.fixture
async def setup_folder_and_file(db_session: Session, setup_users):
    user1, _, _ = setup_users
    folder_data = FolderCreate(name="test_folder")
    folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    class MockUpload:
        def __init__(self, filename, content, content_type):
            self.filename = filename
            self.content = content
            self.content_type = content_type
            self.file = self

        async def read(self, size):
            if self.content:
                chunk = self.content[:size]
                self.content = self.content[size:]
                return chunk
            return b""

    mock_file_content = b"This is a test file content."
    mock_upload = MockUpload("test_file.txt", mock_file_content, "text/plain")

    file, _ = await file_service.create_file(
        db_session, user1.id, mock_upload, folder_id=str(folder.id)
    )
    return folder, file


# Folder Permissions Tests

def test_create_folder_permission(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    permission_data = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, error = permission_service.create_folder_permission(
        db_session, user1.id, permission_data
    )
    assert error is None
    assert permission is not None
    assert permission.user_id == user2.id
    assert permission.folder_id == folder.id
    assert permission.role == RoleEnum.viewer


def test_create_folder_permission_forbidden(db_session: Session, setup_users, setup_folder_and_file):
    _, user2, user3 = setup_users
    folder, _ = setup_folder_and_file

    # User2 (not owner) tries to grant User3 viewer permission
    permission_data = CreateFolderPermission(
        id=folder.id, email=user3.email, role=RoleEnum.viewer
    )
    permission, error = permission_service.create_folder_permission(
        db_session, user2.id, permission_data
    )
    assert permission is None
    assert error == "FORBIDDEN"


def test_create_folder_permission_nonexistent_user(db_session: Session, setup_users, setup_folder_and_file):
    user1, _, _ = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) tries to grant permission to a nonexistent user
    permission_data = CreateFolderPermission(
        id=folder.id, email="nonexistent@example.com", role=RoleEnum.viewer
    )
    permission, error = permission_service.create_folder_permission(
        db_session, user1.id, permission_data
    )
    assert permission is None
    assert error == "NOT_FOUND"


def test_update_folder_permission(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data
    )

    # User1 (owner) updates User2's permission to editor
    update_permission_data = UpdateFolderPermission(
        permission_id=permission.id, role=RoleEnum.editor
    )
    updated_permission, error = permission_service.update_folder_permission(
        db_session, user1.id, update_permission_data
    )
    assert error is None
    assert updated_permission is not None
    assert updated_permission.role == RoleEnum.editor


def test_update_folder_permission_forbidden(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, user3 = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data
    )

    # User3 (not owner) tries to update User2's permission
    update_permission_data = UpdateFolderPermission(
        permission_id=permission.id, role=RoleEnum.editor
    )
    updated_permission, error = permission_service.update_folder_permission(
        db_session, user3.id, update_permission_data
    )
    assert updated_permission is None
    assert error == "FORBIDDEN"


def test_delete_folder_permission(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data
    )

    # User1 (owner) deletes User2's permission
    success, error = permission_service.delete_folder_permission(
        db_session, user1.id, permission.id
    )
    assert error is None
    assert success is True
    assert (
        db_session.query(FolderPermission).filter_by(id=permission.id).first() is None
    )


def test_delete_folder_permission_forbidden(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, user3 = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data
    )

    # User3 (not owner) tries to delete User2's permission
    success, error = permission_service.delete_folder_permission(
        db_session, user3.id, permission.id
    )
    assert success is False
    assert error == "FORBIDDEN"


def test_get_folder_permission_by_id(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    folder, _ = setup_folder_and_file

    create_permission_data = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data
    )

    retrieved_permission, error = permission_service.get_folder_permission_by_id(
        db_session, user2.id, permission.id
    )
    assert error is None
    assert retrieved_permission is not None
    assert retrieved_permission.id == permission.id


def test_get_folder_permission_by_id_not_found(db_session: Session, setup_users):
    user1, _, _ = setup_users
    non_existent_permission_id = uuid.uuid4()
    retrieved_permission, error = permission_service.get_folder_permission_by_id(
        db_session, user1.id, non_existent_permission_id
    )
    assert retrieved_permission is None
    assert error == "NOT_FOUND"


def test_get_folder_permissions_by_folder_id(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, user3 = setup_users
    folder, _ = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data1 = CreateFolderPermission(
        id=folder.id, email=user2.email, role=RoleEnum.viewer
    )
    permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data1
    )

    # User1 (owner) grants User3 editor permission
    create_permission_data2 = CreateFolderPermission(
        id=folder.id, email=user3.email, role=RoleEnum.editor
    )
    permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data2
    )

    # User1 (owner) retrieves all permissions for the folder
    permissions, error = permission_service.get_folder_permissions_by_folder_id(
        db_session, user1.id, folder.id
    )
    assert error is None
    assert len(permissions) == 3  # Owner, User2, User3

    # User2 (viewer) retrieves their own permission for the folder
    permissions_user2, error_user2 = permission_service.get_folder_permissions_by_folder_id(
        db_session, user2.id, folder.id
    )
    assert error_user2 is None
    assert len(permissions_user2) == 1  # Only User2's permission
    assert permissions_user2[0].user_id == user2.id


def test_get_all_folder_permissions(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    folder1, _ = setup_folder_and_file

    # Create another folder for user1
    folder_data2 = FolderCreate(name="test_folder_2")
    folder2, _ = folder_service.create_folder(
        db_session, folder_data2, user_id=user1.id
    )

    # User1 grants User2 viewer permission to folder1
    create_permission_data1 = CreateFolderPermission(
        id=folder1.id, email=user2.email, role=RoleEnum.viewer
    )
    permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data1
    )

    # User1 grants User2 editor permission to folder2
    create_permission_data2 = CreateFolderPermission(
        id=folder2.id, email=user2.email, role=RoleEnum.editor
    )
    permission_service.create_folder_permission(
        db_session, user1.id, create_permission_data2
    )

    # User1 retrieves all their folder permissions
    permissions_user1, error_user1 = permission_service.get_all_folder_permissions(
        db_session, user1.id
    )
    assert error_user1 is None
    assert len(permissions_user1) == 2  # Owner of folder1 and folder2

    # User2 retrieves all their folder permissions
    permissions_user2, error_user2 = permission_service.get_all_folder_permissions(
        db_session, user2.id
    )
    assert error_user2 is None
    assert len(permissions_user2) == 2  # Viewer of folder1, Editor of folder2


# File Permissions Tests

def test_create_file_permission(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    permission_data = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, error = permission_service.create_file_permission(
        db_session, user1.id, permission_data
    )
    assert error is None
    assert permission is not None
    assert permission.user_id == user2.id
    assert permission.file_id == file.id
    assert permission.role == RoleEnum.viewer


def test_create_file_permission_forbidden(db_session: Session, setup_users, setup_folder_and_file):
    _, user2, user3 = setup_users
    _, file = setup_folder_and_file

    # User2 (not owner) tries to grant User3 viewer permission
    permission_data = CreateFilePermission(
        id=file.id, email=user3.email, role=RoleEnum.viewer
    )
    permission, error = permission_service.create_file_permission(
        db_session, user2.id, permission_data
    )
    assert permission is None
    assert error == "FORBIDDEN"


def test_create_file_permission_nonexistent_user(db_session: Session, setup_users, setup_folder_and_file):
    user1, _, _ = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) tries to grant permission to a nonexistent user
    permission_data = CreateFilePermission(
        id=file.id, email="nonexistent@example.com", role=RoleEnum.viewer
    )
    permission, error = permission_service.create_file_permission(
        db_session, user1.id, permission_data
    )
    assert permission is None
    assert error == "NOT_FOUND"


def test_update_file_permission(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_file_permission(
        db_session, user1.id, create_permission_data
    )

    # User1 (owner) updates User2's permission to editor
    update_permission_data = UpdateFilePermission(
        permission_id=permission.id, role=RoleEnum.editor
    )
    updated_permission, error = permission_service.update_file_permission(
        db_session, user1.id, update_permission_data
    )
    assert error is None
    assert updated_permission is not None
    assert updated_permission.role == RoleEnum.editor


def test_update_file_permission_forbidden(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, user3 = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_file_permission(
        db_session, user1.id, create_permission_data
    )

    # User3 (not owner) tries to update User2's permission
    update_permission_data = UpdateFilePermission(
        permission_id=permission.id, role=RoleEnum.editor
    )
    updated_permission, error = permission_service.update_file_permission(
        db_session, user3.id, update_permission_data
    )
    assert updated_permission is None
    assert error == "FORBIDDEN"


def test_delete_file_permission(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_file_permission(
        db_session, user1.id, create_permission_data
    )

    # User1 (owner) deletes User2's permission
    success, error = permission_service.delete_file_permission(
        db_session, user1.id, permission.id
    )
    assert error is None
    assert success is True
    assert (
        db_session.query(FilePermission).filter_by(id=permission.id).first() is None
    )


def test_delete_file_permission_forbidden(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, user3 = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_file_permission(
        db_session, user1.id, create_permission_data
    )

    # User3 (not owner) tries to delete User2's permission
    success, error = permission_service.delete_file_permission(
        db_session, user3.id, permission.id
    )
    assert success is False
    assert error == "FORBIDDEN"


def test_get_file_permission_by_id(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    _, file = setup_folder_and_file

    create_permission_data = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission, _ = permission_service.create_file_permission(
        db_session, user1.id, create_permission_data
    )

    retrieved_permission, error = permission_service.get_file_permission_by_id(
        db_session, user2.id, permission.id
    )
    assert error is None
    assert retrieved_permission is not None
    assert retrieved_permission.id == permission.id


def test_get_file_permission_by_id_not_found(db_session: Session, setup_users):
    user1, _, _ = setup_users
    non_existent_permission_id = uuid.uuid4()
    retrieved_permission, error = permission_service.get_file_permission_by_id(
        db_session, user1.id, non_existent_permission_id
    )
    assert retrieved_permission is None
    assert error == "NOT_FOUND"


def test_get_file_permissions_by_file_id(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, user3 = setup_users
    _, file = setup_folder_and_file

    # User1 (owner) grants User2 viewer permission
    create_permission_data1 = CreateFilePermission(
        id=file.id, email=user2.email, role=RoleEnum.viewer
    )
    permission_service.create_file_permission(
        db_session, user1.id, create_permission_data1
    )

    # User1 (owner) grants User3 editor permission
    create_permission_data2 = CreateFilePermission(
        id=file.id, email=user3.email, role=RoleEnum.editor
    )
    permission_service.create_file_permission(
        db_session, user1.id, create_permission_data2
    )

    # User1 (owner) retrieves all permissions for the file
    permissions, error = permission_service.get_file_permissions_by_file_id(
        db_session, user1.id, file.id
    )
    assert error is None
    assert len(permissions) == 3  # Owner, User2, User3

    # User2 (viewer) retrieves their own permission for the file
    permissions_user2, error_user2 = permission_service.get_file_permissions_by_file_id(
        db_session, user2.id, file.id
    )
    assert error_user2 is None
    assert len(permissions_user2) == 1  # Only User2's permission
    assert permissions_user2[0].user_id == user2.id


def test_get_all_file_permissions(db_session: Session, setup_users, setup_folder_and_file):
    user1, user2, _ = setup_users
    _, file1 = setup_folder_and_file

    # Create another file for user1
    folder_data = FolderCreate(name="another_folder")
    folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )
    file_data2 = CreateFile(
        name="test_file_2",
        folder_id=folder.id,
        file="/tmp/test_file_2.txt",
        mime_type="text/plain",
    )
    file2, _ = file_service.create_file(db_session, file_data2, user_id=user1.id)

    # User1 grants User2 viewer permission to file1
    create_permission_data1 = CreateFilePermission(
        id=file1.id, email=user2.email, role=RoleEnum.viewer
    )
    permission_service.create_file_permission(
        db_session, user1.id, create_permission_data1
    )

    # User1 grants User2 editor permission to file2
    create_permission_data2 = CreateFilePermission(
        id=file2.id, email=user2.email, role=RoleEnum.editor
    )
    permission_service.create_file_permission(
        db_session, user1.id, create_permission_data2
    )

    # User1 retrieves all their file permissions
    permissions_user1, error_user1 = permission_service.get_all_file_permissions(
        db_session, user1.id
    )
    assert error_user1 is None
    assert len(permissions_user1) == 2  # Owner of file1 and file2

    # User2 retrieves all their file permissions
    permissions_user2, error_user2 = permission_service.get_all_file_permissions(
        db_session, user2.id
    )
    assert error_user2 is None
    assert len(permissions_user2) == 2  # Viewer of file1, Editor of file2
    """
