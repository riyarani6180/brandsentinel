
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Store the SQLite database inside the backend folder
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "brandsentinel.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()


# Dependency for database access in API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
