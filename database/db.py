"""
Database configuration and initialization
SQLite database setup with SQLAlchemy
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
DB_PATH = os.path.join(DB_DIR, 'app.db')
DATABASE_URL = f'sqlite:///{DB_PATH}'

# Create SQLAlchemy engine
# check_same_thread=False is required for SQLite to work with Streamlit
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False},
    echo=False  # Set to True for SQL query logging during development
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-safe scoped session for Streamlit
ScopedSession = scoped_session(SessionLocal)


def init_db():
    """
    Initialize the database by creating all tables defined in models.
    This function should be called once when the application starts.
    """
    # Ensure database directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at: {DB_PATH}")


def get_db():
    """
    Dependency function to get a database session.
    Use this in a context manager or ensure proper cleanup.
    
    Usage:
        db = get_db()
        try:
            # Use db session
            pass
        finally:
            db.close()
    """
    db = ScopedSession()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


def close_db(db):
    """
    Close the database session properly.
    
    Args:
        db: SQLAlchemy session object
    """
    if db:
        db.close()
