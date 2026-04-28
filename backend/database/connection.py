"""
Database connection and session management
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings
from backend.models.experiment import Base

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.database_url else {}
    ),
    echo=settings.debug,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def reset_db():
    """Drop and recreate all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session (for non-FastAPI contexts)

    Returns:
        Database session (must be closed manually)
    """
    return SessionLocal()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
