#!/usr/bin/env python3
"""
TouchLine Database Manager
Simple CLI tool to manage the database
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "touchline.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_alerts(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Get alerts, optionally filtered by user"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM alerts WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT * FROM alerts")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_matches(self) -> List[Dict[str, Any]]:
        """Get all matches"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM matches ORDER BY start_time DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_alert_history(self, alert_id: int = None) -> List[Dict[str, Any]]:
        """Get alert history"""
        cursor = self.conn.cursor()
        if alert_id:
            cursor.execute("SELECT * FROM alert_history WHERE alert_id = ?", (alert_id,))
        else:
            cursor.execute("SELECT * FROM alert_history ORDER BY triggered_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def create_sample_data(self):
        """Create sample data for testing"""
        cursor = self.conn.cursor()
        
        # Create sample user
        cursor.execute("""
            INSERT OR IGNORE INTO users (email, username, hashed_password, phone_number, full_name, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("demo@touchline.com", "demo_user", "hashed_password", "+1234567890", "Demo User", True))
        
        # Create sample match
        cursor.execute("""
            INSERT OR IGNORE INTO matches (external_id, home_team, away_team, league, start_time, status, home_score, away_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("demo_match_1", "Manchester United", "Liverpool", "Premier League", datetime.now(), "live", 1, 2))
        
        # Create sample alert
        cursor.execute("""
            INSERT OR IGNORE INTO alerts (user_id, name, alert_type, team, condition, threshold, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, "Liverpool Goal Alert", "goals", "Liverpool", "Team scores", 1.0, True))
        
        self.conn.commit()
        print("✅ Sample data created!")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # User stats
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['users'] = cursor.fetchone()[0]
        
        # Alert stats
        cursor.execute("SELECT COUNT(*) FROM alerts")
        stats['alerts'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_active = 1")
        stats['active_alerts'] = cursor.fetchone()[0]
        
        # Match stats
        cursor.execute("SELECT COUNT(*) FROM matches")
        stats['matches'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE status = 'live'")
        stats['live_matches'] = cursor.fetchone()[0]
        
        # Alert history stats
        cursor.execute("SELECT COUNT(*) FROM alert_history")
        stats['alert_triggers'] = cursor.fetchone()[0]
        
        return stats
    
    def export_data(self, table: str = None) -> Dict[str, Any]:
        """Export data to JSON"""
        if table:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            return [dict(row) for row in cursor.fetchall()]
        else:
            # Export all tables
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            data = {}
            for table_name in tables:
                cursor.execute(f"SELECT * FROM {table_name}")
                data[table_name] = [dict(row) for row in cursor.fetchall()]
            
            return data
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """CLI interface"""
    import sys
    
    db = DatabaseManager()
    
    if len(sys.argv) < 2:
        print("TouchLine Database Manager")
        print("Usage: python db_manager.py <command> [args]")
        print("\nCommands:")
        print("  stats                    - Show database statistics")
        print("  users                    - List all users")
        print("  alerts [user_id]         - List alerts (optionally for user)")
        print("  matches                  - List matches")
        print("  history [alert_id]       - List alert history")
        print("  sample                   - Create sample data")
        print("  export [table]           - Export data to JSON")
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        stats = db.get_stats()
        print("📊 Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif command == "users":
        users = db.get_users()
        print("👥 Users:")
        for user in users:
            print(f"  ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
    
    elif command == "alerts":
        user_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        alerts = db.get_alerts(user_id)
        print("🔔 Alerts:")
        for alert in alerts:
            print(f"  ID: {alert['id']}, Name: {alert['name']}, Type: {alert['alert_type']}, Active: {alert['is_active']}")
    
    elif command == "matches":
        matches = db.get_matches()
        print("⚽ Matches:")
        for match in matches:
            print(f"  ID: {match['id']}, {match['home_team']} vs {match['away_team']}, Status: {match['status']}")
    
    elif command == "history":
        alert_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        history = db.get_alert_history(alert_id)
        print("📈 Alert History:")
        for entry in history:
            print(f"  Alert ID: {entry['alert_id']}, Triggered: {entry['triggered_at']}, Message: {entry['trigger_message']}")
    
    elif command == "sample":
        db.create_sample_data()
    
    elif command == "export":
        table = sys.argv[2] if len(sys.argv) > 2 else None
        data = db.export_data(table)
        print(json.dumps(data, indent=2, default=str))
    
    else:
        print(f"Unknown command: {command}")
    
    db.close()

if __name__ == "__main__":
    main()
