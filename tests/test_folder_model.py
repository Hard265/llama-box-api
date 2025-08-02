from app.models.folder import Folder
from app.models.user import User


def test_create_folder(db_session):
    user = User(email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    folder = Folder(name="test_folder", parent_id=None)
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)

    assert folder.id is not None
    assert folder.name == "test_folder"
    assert folder.parent_id is None
