from app.models.permission import FilePermission, FolderPermission, RoleEnum
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User


def test_create_file_permission(db_session):
    user = User(email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    folder = Folder(name="test_folder", parent_id=None)
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)

    file = File(
        name="test_file",
        folder_id=folder.id,
        file="/path/to/file",
        mime_type="text/plain",
        ext=".txt",
        size=123,
    )
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)

    permission = FilePermission(user_id=user.id, file_id=file.id, role=RoleEnum.viewer)
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)

    assert permission.id is not None
    assert permission.user_id == user.id
    assert permission.file_id == file.id
    assert permission.role == RoleEnum.viewer


def test_create_folder_permission(db_session):
    user = User(email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    folder = Folder(name="test_folder", parent_id=None)
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)

    permission = FolderPermission(
        user_id=user.id, folder_id=folder.id, role=RoleEnum.viewer
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)

    assert permission.id is not None
    assert permission.user_id == user.id
    assert permission.folder_id == folder.id
    assert permission.role == RoleEnum.viewer
