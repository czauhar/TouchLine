#!/usr/bin/env python3
"""
PostgreSQL Migration Script
Migrates data from SQLite to PostgreSQL
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

# Database URLs
SQLITE_DB = "touchline.db"
POSTGRES_URL = "postgresql://touchline:touchline123@localhost:5432/touchline"

def migrate_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Starting PostgreSQL migration...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    postgres_conn = psycopg2.connect(POSTGRES_URL)
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Create tables in PostgreSQL (using SQLAlchemy models)
        print("📊 Creating PostgreSQL tables...")
        from app.database import engine
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        
        # Migrate users
        print("👥 Migrating users...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            postgres_cursor.execute("""
                INSERT INTO users (id, email, username, hashed_password, phone_number, 
                                 full_name, role, preferences, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                user['id'], user['email'], user['username'], user['hashed_password'],
                user['phone_number'], user.get('full_name'), user.get('role', 'user'),
                user.get('preferences'), user['is_active'], user['created_at'],
                user.get('updated_at', user['created_at'])
            ))
        
        # Migrate matches
        print("⚽ Migrating matches...")
        sqlite_cursor.execute("SELECT * FROM matches")
        matches = sqlite_cursor.fetchall()
        
        for match in matches:
            postgres_cursor.execute("""
                INSERT INTO matches (id, external_id, home_team, away_team, league,
                                   start_time, status, home_score, away_score, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                match['id'], match['external_id'], match['home_team'], match['away_team'],
                match['league'], match['start_time'], match['status'], match['home_score'],
                match['away_score'], match['created_at']
            ))
        
        # Migrate alerts
        print("🔔 Migrating alerts...")
        sqlite_cursor.execute("SELECT * FROM alerts")
        alerts = sqlite_cursor.fetchall()
        
        for alert in alerts:
            postgres_cursor.execute("""
                INSERT INTO alerts (id, user_id, name, alert_type, team, condition,
                                  threshold, time_window, user_phone, is_active, created_at,
                                  trigger_count, last_triggered_at, conditions_json, player_id, player_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                alert['id'], alert['user_id'], alert['name'], alert['alert_type'],
                alert['team'], alert['condition'], alert['threshold'], alert.get('time_window'),
                alert.get('user_phone'), alert['is_active'], alert['created_at'],
                alert.get('trigger_count', 0), alert.get('last_triggered_at'),
                alert.get('conditions_json'), alert.get('player_id'), alert.get('player_name')
            ))
        
        # Migrate alert history
        print("📈 Migrating alert history...")
        sqlite_cursor.execute("SELECT * FROM alert_history")
        alert_history = sqlite_cursor.fetchall()
        
        for entry in alert_history:
            postgres_cursor.execute("""
                INSERT INTO alert_history (id, alert_id, match_id, triggered_at,
                                         trigger_message, sms_sent, sms_message_id, match_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                entry['id'], entry['alert_id'], entry['match_id'], entry['triggered_at'],
                entry['trigger_message'], entry['sms_sent'], entry.get('sms_message_id'),
                entry.get('match_data')
            ))
        
        # Commit changes
        postgres_conn.commit()
        
        # Verify migration
        print("✅ Verifying migration...")
        postgres_cursor.execute("SELECT COUNT(*) FROM users")
        user_count = postgres_cursor.fetchone()[0]
        
        postgres_cursor.execute("SELECT COUNT(*) FROM matches")
        match_count = postgres_cursor.fetchone()[0]
        
        postgres_cursor.execute("SELECT COUNT(*) FROM alerts")
        alert_count = postgres_cursor.fetchone()[0]
        
        print(f"📊 Migration Results:")
        print(f"   Users: {user_count}")
        print(f"   Matches: {match_count}")
        print(f"   Alerts: {alert_count}")
        
        print("✅ PostgreSQL migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        postgres_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    migrate_to_postgres()
