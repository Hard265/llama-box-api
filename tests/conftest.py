
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import os

# Import all models to ensure they are registered with SQLAlchemy's Base

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    os.remove("./test.db")

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin_nested()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield session
    session.rollback()
    session.close()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    from app.services.user import create_user
    from app.schemas.user import UserCreate
    import uuid

    user_data = UserCreate(email=f"test_{uuid.uuid4()}@example.com", password="password")
    user = create_user(user_data, db_session)
    db_session.commit()
    db_session.refresh(user)
    return user






