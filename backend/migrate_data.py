#!/usr/bin/env python3
"""
Data Migration Script
Migrates data from SQLite to PostgreSQL
"""

import sqlite3
import psycopg2
from datetime import datetime

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Starting data migration...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('touchline.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    postgres_conn = psycopg2.connect('postgresql://touchline:touchline123@localhost:5432/touchline')
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Migrate users
        print("👥 Migrating users...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            # Convert SQLite row to dict
            user_dict = dict(user)
            
            postgres_cursor.execute("""
                INSERT INTO users (id, email, username, hashed_password, phone_number, 
                                 full_name, role, preferences, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                user_dict['id'], user_dict['email'], user_dict['username'], 
                user_dict['hashed_password'], user_dict['phone_number'],
                user_dict.get('full_name'), user_dict.get('role', 'user'),
                user_dict.get('preferences'), user_dict['is_active'], 
                user_dict['created_at'], user_dict.get('updated_at', user_dict['created_at'])
            ))
        
        # Migrate matches
        print("⚽ Migrating matches...")
        sqlite_cursor.execute("SELECT * FROM matches")
        matches = sqlite_cursor.fetchall()
        
        for match in matches:
            match_dict = dict(match)
            
            postgres_cursor.execute("""
                INSERT INTO matches (id, external_id, home_team, away_team, league,
                                   start_time, status, home_score, away_score, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                match_dict['id'], match_dict['external_id'], match_dict['home_team'], 
                match_dict['away_team'], match_dict['league'], match_dict['start_time'], 
                match_dict['status'], match_dict['home_score'], match_dict['away_score'], 
                match_dict['created_at']
            ))
        
        # Migrate alerts
        print("🔔 Migrating alerts...")
        sqlite_cursor.execute("SELECT * FROM alerts")
        alerts = sqlite_cursor.fetchall()
        
        for alert in alerts:
            alert_dict = dict(alert)
            
            postgres_cursor.execute("""
                INSERT INTO alerts (id, user_id, name, alert_type, team, condition,
                                  threshold, time_window, user_phone, is_active, created_at,
                                  trigger_count, last_triggered_at, conditions_json, player_id, player_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                alert_dict['id'], alert_dict['user_id'], alert_dict['name'], 
                alert_dict['alert_type'], alert_dict['team'], alert_dict['condition'], 
                alert_dict['threshold'], alert_dict.get('time_window'), 
                alert_dict.get('user_phone'), alert_dict['is_active'], 
                alert_dict['created_at'], alert_dict.get('trigger_count', 0), 
                alert_dict.get('last_triggered_at'), alert_dict.get('conditions_json'), 
                alert_dict.get('player_id'), alert_dict.get('player_name')
            ))
        
        # Migrate alert history
        print("📈 Migrating alert history...")
        sqlite_cursor.execute("SELECT * FROM alert_history")
        alert_history = sqlite_cursor.fetchall()
        
        for entry in alert_history:
            entry_dict = dict(entry)
            
            postgres_cursor.execute("""
                INSERT INTO alert_history (id, alert_id, match_id, triggered_at,
                                         trigger_message, sms_sent, sms_message_id, match_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                entry_dict['id'], entry_dict['alert_id'], entry_dict['match_id'], 
                entry_dict['triggered_at'], entry_dict['trigger_message'], 
                entry_dict['sms_sent'], entry_dict.get('sms_message_id'), 
                entry_dict.get('match_data')
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
        
        postgres_cursor.execute("SELECT COUNT(*) FROM alert_history")
        history_count = postgres_cursor.fetchone()[0]
        
        print(f"📊 Migration Results:")
        print(f"   Users: {user_count}")
        print(f"   Matches: {match_count}")
        print(f"   Alerts: {alert_count}")
        print(f"   Alert History: {history_count}")
        
        print("✅ Data migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        postgres_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    migrate_data()
