import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User


def test_create_user(db_session):
    user = User(email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.password == "password"
    assert user.is_active is True


def test_duplicate_email(db_session):
    user1 = User(email="test@example.com", password="password")
    db_session.add(user1)
    db_session.commit()

    user2 = User(email="test@example.com", password="password2")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_is_active_defaults_to_true(db_session):
    user = User(email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.is_active is True
