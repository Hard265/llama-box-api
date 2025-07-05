
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User

def test_create_file(db_session):
    user = User(email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    folder = Folder(name="test_folder", parent_id=None)
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)

    file = File(name="test_file", folder_id=folder.id, file="/path/to/file", mime_type="text/plain", ext=".txt", size=123)
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)

    assert file.id is not None
    assert file.name == "test_file"
    assert file.folder_id == folder.id
