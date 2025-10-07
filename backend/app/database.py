from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base
from .core.config import settings

# Use settings for database URL - prefer PostgreSQL if available
DATABASE_URL = settings.POSTGRES_URL or settings.DATABASE_URL

# Check if we're using PostgreSQL
IS_POSTGRES = "postgresql" in DATABASE_URL

# Create engine with optimized connection pool settings for memory efficiency
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Reduced from 10 to save memory
    max_overflow=10,  # Reduced from 20 to save memory
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=1800,  # Recycle connections after 30 minutes (reduced from 1 hour)
    pool_pre_ping=True,  # Validate connections before use
    echo=False,  # Disable SQL logging to save memory
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!") 