from sqlmodel import create_engine, Session
from app.config import settings

# Create engine with connection pooling for Neon PostgreSQL
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,          # Maintain 5 connections in pool
    max_overflow=10       # Allow up to 10 additional connections
)


def get_session():
    """Dependency function to provide database session."""
    with Session(engine) as session:
        yield session
