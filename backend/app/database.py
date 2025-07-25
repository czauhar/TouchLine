from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base
from .core.config import settings

# Use settings for database URL, but ensure correct path for SQLite
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith('sqlite:///./'):
    # Convert relative path to absolute path in app directory
    DATABASE_URL = DATABASE_URL.replace('sqlite:///./', 'sqlite:///app/')

# Create engine
engine = create_engine(DATABASE_URL)

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