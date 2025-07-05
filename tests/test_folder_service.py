
import uuid

import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.folder import FolderCreate, FolderUpdate
from app.services import folder as folder_service


@pytest.fixture
def setup_users(db_session: Session):
    user1 = User(email="test1@example.com", password="password")
    user2 = User(email="test2@example.com", password="password")
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    return user1, user2


def test_create_folder(db_session: Session, setup_users):
    user1, _ = setup_users
    folder_data = FolderCreate(name="test_folder")
    folder, error = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )
    assert error is None
    assert folder is not None
    assert folder.name == "test_folder"
    assert folder.parent_id is None
    assert len(folder.permissions) == 1
    assert folder.permissions[0].user_id == user1.id
    assert folder.permissions[0].role == "owner"


def test_create_subfolder(db_session: Session, setup_users):
    user1, _ = setup_users
    parent_folder_data = FolderCreate(name="parent_folder")
    parent_folder, error = folder_service.create_folder(
        db_session, parent_folder_data, user_id=user1.id
    )
    assert error is None
    assert parent_folder is not None

    subfolder_data = FolderCreate(name="subfolder", parent_id=parent_folder.id)
    subfolder, error = folder_service.create_folder(
        db_session, subfolder_data, user_id=user1.id
    )
    assert error is None
    assert subfolder is not None
    assert subfolder.name == "subfolder"
    assert subfolder.parent_id == parent_folder.id


def test_create_folder_with_nonexistent_parent(db_session: Session, setup_users):
    user1, _ = setup_users
    non_existent_parent_id = uuid.uuid4()
    folder_data = FolderCreate(name="test_folder", parent_id=non_existent_parent_id)
    folder, error = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )
    assert folder is None
    assert error == "NOT_FOUND"


def test_get_folder(db_session: Session, setup_users):
    user1, _ = setup_users
    folder_data = FolderCreate(name="test_folder")
    created_folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    retrieved_folder = folder_service.get_folder(
        db_session, user_id=user1.id, id=created_folder.id
    )
    assert retrieved_folder is not None
    assert retrieved_folder.id == created_folder.id


def test_get_folder_no_permission(db_session: Session, setup_users):
    user1, user2 = setup_users
    folder_data = FolderCreate(name="test_folder")
    created_folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    retrieved_folder = folder_service.get_folder(
        db_session, user_id=user2.id, id=created_folder.id
    )
    assert retrieved_folder is None


def test_get_folders(db_session: Session, setup_users):
    user1, _ = setup_users
    folder_data1 = FolderCreate(name="folder1")
    folder_data2 = FolderCreate(name="folder2")
    folder_service.create_folder(db_session, folder_data1, user_id=user1.id)
    folder_service.create_folder(db_session, folder_data2, user_id=user1.id)

    folders = folder_service.get_folders(db_session, user_id=user1.id).all()
    assert len(folders) == 2


def test_get_subfolders(db_session: Session, setup_users):
    user1, _ = setup_users
    parent_folder_data = FolderCreate(name="parent")
    parent_folder, _ = folder_service.create_folder(
        db_session, parent_folder_data, user_id=user1.id
    )

    subfolder_data1 = FolderCreate(name="sub1", parent_id=parent_folder.id)
    subfolder_data2 = FolderCreate(name="sub2", parent_id=parent_folder.id)
    folder_service.create_folder(db_session, subfolder_data1, user_id=user1.id)
    folder_service.create_folder(db_session, subfolder_data2, user_id=user1.id)

    subfolders = folder_service.get_folders(
        db_session, user_id=user1.id, parent_id=parent_folder.id
    ).all()
    assert len(subfolders) == 2


def test_update_folder(db_session: Session, setup_users):
    user1, _ = setup_users
    folder_data = FolderCreate(name="original_name")
    folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    update_data = FolderUpdate(id=folder.id, name="updated_name")
    updated_folder, error = folder_service.update_folder(
        db_session, user_id=user1.id, folder_update_schema=update_data, input_data=update_data
    )
    assert error is None
    assert updated_folder is not None
    assert updated_folder.name == "updated_name"


def test_update_folder_no_permission(db_session: Session, setup_users):
    user1, user2 = setup_users
    folder_data = FolderCreate(name="original_name")
    folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    update_data = FolderUpdate(id=folder.id, name="updated_name")
    updated_folder, error = folder_service.update_folder(
        db_session, user_id=user2.id, folder_update_schema=update_data, input_data=update_data
    )
    assert updated_folder is None
    assert error == "NOT_FOUND"


def test_delete_folder(db_session: Session, setup_users):
    user1, _ = setup_users
    folder_data = FolderCreate(name="to_be_deleted")
    folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    success, error = folder_service.delete_folder(
        db_session, user_id=user1.id, folder_id=folder.id
    )
    assert error is None
    assert success is True
    assert folder_service.get_folder(db_session, user_id=user1.id, id=folder.id) is None


def test_delete_folder_no_permission(db_session: Session, setup_users):
    user1, user2 = setup_users
    folder_data = FolderCreate(name="test_folder")
    folder, _ = folder_service.create_folder(
        db_session, folder_data, user_id=user1.id
    )

    success, error = folder_service.delete_folder(
        db_session, user_id=user2.id, folder_id=folder.id
    )
    assert success is False
    assert error == "FORBIDDEN"
