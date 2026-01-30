"""Database engine setup and session management."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from ..config import DATABASE_URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.

    Yields:
        Database session that auto-closes after use

    Usage:
        with get_db() as db:
            # use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Should be called once at application startup.
    """
    # Import models to ensure they're registered
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
