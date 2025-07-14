import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.folder import Folder
from app.models.file import File
from app.models.permission import FolderPermission, FilePermission, RoleEnum
from app.services.move import move_files, move_folders


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


def test_move_folder(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    moved_folders = move_folders(
        db_session, source_folders=[folder1], destination_folder=folder2, user=user1
    )

    assert len(moved_folders) == 1
    assert moved_folders[0].parent_id == folder2.id


def test_move_folder_into_subfolder(db_session: Session, setup_users, setup_folders):
    user1, _ = setup_users
    folder1, folder2 = setup_folders

    subfolder = Folder(name="subfolder", parent_id=folder1.id)
    db_session.add(subfolder)
    db_session.commit()
    db_session.refresh(subfolder)

    with pytest.raises(ValueError):
        move_folders(
            db_session, source_folders=[folder1], destination_folder=subfolder, user=user1
        )


def test_move_multiple_files(db_session: Session, setup_users, setup_folders):
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

    permission1 = FilePermission(file_id=file1.id, user_id=user1.id, role=RoleEnum.owner)
    permission2 = FilePermission(file_id=file2.id, user_id=user1.id, role=RoleEnum.owner)
    db_session.add_all([permission1, permission2])
    db_session.commit()

    moved_files = move_files(
        db_session, source_files=[file1, file2], destination_folder=folder2, user=user1
    )

    assert len(moved_files) == 2
    assert moved_files[0].folder_id == folder2.id
    assert moved_files[1].folder_id == folder2.id


def test_move_multiple_folders(db_session: Session, setup_users, setup_folders):
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

    moved_folders = move_folders(
        db_session, source_folders=[folder1, folder3], destination_folder=folder2, user=user1
    )

    assert len(moved_folders) == 2
    assert moved_folders[0].parent_id == folder2.id
    assert moved_folders[1].parent_id == folder2.id
