from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./nucleus_cloud.db"  # For development; consider PostgreSQL for production.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # Needed for SQLite

with engine.connect() as conn:
    conn.execute(text("PRAGMA foreign_keys=ON"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
