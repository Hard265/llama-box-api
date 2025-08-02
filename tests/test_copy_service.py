import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.folder import Folder
from app.models.file import File
from app.models.permission import FolderPermission, FilePermission, RoleEnum
from app.services.copy import CopyService


@pytest.fixture
def setup_users(db_session: Session):
    user1 = User(email="test1@example.com", password="password")
    user2 = User(email="test2@example.com", password="password")
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    return user1, user2


@pytest.fixture
def setup_folders(db_session: Session, setup_users):
    user1, _ = setup_users
    folder1 = Folder(name="folder1")
    folder2 = Folder(name="folder2")
    db_session.add_all([folder1, folder2])
    db_session.commit()
    db_session.refresh(folder1)
    db_session.refresh(folder2)

    permission1 = FolderPermission(
        folder_id=folder1.id, user_id=user1.id, role=RoleEnum.owner
    )
    permission2 = FolderPermission(
        folder_id=folder2.id, user_id=user1.id, role=RoleEnum.owner
    )
    db_session.add_all([permission1, permission2])
    db_session.commit()

    return folder1, folder2


def test_copy_folder(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    copy_service = CopyService(db_session)
    copied_folder = copy_service.copy_folder(
        source_folder=folder1, destination_parent=folder2, user=user1
    )

    assert copied_folder is not None
    assert copied_folder.name == "folder1 (Copy)"
    assert copied_folder.parent_id == folder2.id
    assert copied_folder.owner.id == user1.id


def test_copy_folder_with_children(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    subfolder = Folder(name="subfolder", parent_id=folder1.id)
    db_session.add(subfolder)
    db_session.commit()
    db_session.refresh(subfolder)

    file = File(
        name="file",
        folder_id=folder1.id,
        file="/path/to/file",
        mime_type="text/plain",
        ext="txt",
        size=123,
    )
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)

    permission = FilePermission(file_id=file.id, user_id=user1.id, role=RoleEnum.owner)
    db_session.add(permission)
    db_session.commit()

    copy_service = CopyService(db_session)
    copied_folder = copy_service.copy_folder(
        source_folder=folder1, destination_parent=folder2, user=user1
    )

    assert copied_folder is not None
    assert len(copied_folder.folders) == 1
    assert copied_folder.folders[0].name == "subfolder"
    assert len(copied_folder.files) == 1
    assert copied_folder.files[0].name == "file (Copy)"


def test_copy_multiple_folders(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    folder3 = Folder(name="folder3")
    db_session.add(folder3)
    db_session.commit()
    db_session.refresh(folder3)

    permission = FolderPermission(
        folder_id=folder3.id, user_id=user1.id, role=RoleEnum.owner
    )
    db_session.add(permission)
    db_session.commit()

    copy_service = CopyService(db_session)
    copied_folders = []
    for folder in [folder1, folder3]:
        copied_folder = copy_service.copy_folder(
            source_folder=folder, destination_parent=folder2, user=user1
        )
        copied_folders.append(copied_folder)

    assert len(copied_folders) == 2
    assert copied_folders[0].name == "folder1 (Copy)"
    assert copied_folders[1].name == "folder3 (Copy)"
    assert copied_folders[0].parent_id == folder2.id
    assert copied_folders[1].parent_id == folder2.id


def test_copy_multiple_files(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    file1 = File(
        name="file1",
        folder_id=folder1.id,
        file="/path/to/file1",
        mime_type="text/plain",
        ext="txt",
        size=123,
    )
    file2 = File(
        name="file2",
        folder_id=folder1.id,
        file="/path/to/file2",
        mime_type="text/plain",
        ext="txt",
        size=456,
    )
    db_session.add_all([file1, file2])
    db_session.commit()
    db_session.refresh(file1)
    db_session.refresh(file2)

    permission1 = FilePermission(
        file_id=file1.id, user_id=user1.id, role=RoleEnum.owner
    )
    permission2 = FilePermission(
        file_id=file2.id, user_id=user1.id, role=RoleEnum.owner
    )
    db_session.add_all([permission1, permission2])
    db_session.commit()

    copy_service = CopyService(db_session)
    copied_files = []
    for file in [file1, file2]:
        copied_file = copy_service.copy_file(
            source_file=file, destination_folder=folder2, user=user1
        )
        copied_files.append(copied_file)

    assert len(copied_files) == 2
    assert copied_files[0].name == "file1 (Copy)"
    assert copied_files[1].name == "file2 (Copy)"
    assert copied_files[0].folder_id == folder2.id
    assert copied_files[1].folder_id == folder2.id


def test_copy_folder_name_conflict(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    existing_folder = Folder(name="folder1 (Copy)", parent_id=folder2.id)
    db_session.add(existing_folder)
    db_session.commit()

    copy_service = CopyService(db_session)
    copied_folder = copy_service.copy_folder(
        source_folder=folder1, destination_parent=folder2, user=user1
    )

    assert copied_folder is not None
    assert copied_folder.name == "folder1 (Copy) (1)"


def test_copy_file_name_conflict(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    file1 = File(
        name="file1",
        folder_id=folder1.id,
        file="/path/to/file1",
        mime_type="text/plain",
        ext="txt",
        size=123,
    )
    db_session.add(file1)
    db_session.commit()
    db_session.refresh(file1)

    permission = FilePermission(file_id=file1.id, user_id=user1.id, role=RoleEnum.owner)
    db_session.add(permission)
    db_session.commit()

    existing_file = File(
        name="file1 (Copy)",
        folder_id=folder2.id,
        file="/path/to/existing_file",
        mime_type="text/plain",
        ext="txt",
        size=456,
    )
    db_session.add(existing_file)
    db_session.commit()

    copy_service = CopyService(db_session)
    copied_file = copy_service.copy_file(
        source_file=file1, destination_folder=folder2, user=user1
    )

    assert copied_file is not None
    assert copied_file.name == "file1 (Copy) (1)"
