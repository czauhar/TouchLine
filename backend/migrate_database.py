#!/usr/bin/env python3
"""
Database migration script to add new tables for efficient data storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base, MatchCache, MatchMetrics

def migrate_database():
    """Create new tables for efficient data storage"""
    print("🔄 Starting database migration...")
    
    try:
        # Create new tables
        print("📊 Creating MatchCache table...")
        MatchCache.__table__.create(engine, checkfirst=True)
        
        print("📈 Creating MatchMetrics table...")
        MatchMetrics.__table__.create(engine, checkfirst=True)
        
        print("✅ Database migration completed successfully!")
        print("📋 New tables created:")
        print("   - match_cache: For caching match data")
        print("   - match_metrics: For structured metrics storage")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database() 