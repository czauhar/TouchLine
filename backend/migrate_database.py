#!/usr/bin/env python3
"""
Database migration script for TouchLine
Adds missing columns to existing tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models import Base, MatchCache, MatchMetrics

def migrate_database():
    """Run database migrations"""
    print("🔄 Starting database migration...")
    
    # Get database engine
    db = next(get_db())
    
    try:
        # Check if player_id and player_name columns exist in alerts table
        result = db.execute(text("PRAGMA table_info(alerts)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Add missing columns if they don't exist
        if 'player_id' not in columns:
            print("📝 Adding player_id column to alerts table...")
            db.execute(text("ALTER TABLE alerts ADD COLUMN player_id INTEGER"))
        
        if 'player_name' not in columns:
            print("📝 Adding player_name column to alerts table...")
            db.execute(text("ALTER TABLE alerts ADD COLUMN player_name VARCHAR"))
        
        # Create new tables if they don't exist
        print("📊 Creating MatchCache table...")
        Base.metadata.create_all(bind=db.bind, tables=[MatchCache.__table__])
        
        print("📈 Creating MatchMetrics table...")
        Base.metadata.create_all(bind=db.bind, tables=[MatchMetrics.__table__])
        
        db.commit()
        print("✅ Database migration completed successfully!")
        print("📋 New tables created:")
        print("   - match_cache: For caching match data")
        print("   - match_metrics: For structured metrics storage")
        print("📋 Columns added to alerts table:")
        print("   - player_id: For player-specific alerts")
        print("   - player_name: For player name display")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database() 