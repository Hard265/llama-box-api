from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./nucleus_cloud.db"  # For development; consider PostgreSQL for production.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
