#!/usr/bin/env python3
"""
TouchLine Database Query Interface
Interactive database querying and analytics
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

class DatabaseQuerier:
    """Interactive database querying interface"""
    
    def __init__(self, db_type="sqlite", db_path="touchline.db"):
        self.db_type = db_type
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        if db_type == "sqlite":
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        elif db_type == "postgres":
            self.conn = psycopg2.connect("postgresql://touchline:touchline123@localhost:5432/touchline")
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def get_user_analytics(self) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        try:
            if self.db_type == "sqlite":
                # SQLite queries
                self.cursor.execute("""
                    SELECT 
                        u.id, u.username, u.email, u.full_name, u.created_at,
                        COUNT(a.id) as total_alerts,
                        COUNT(CASE WHEN a.is_active = 1 THEN 1 END) as active_alerts,
                        COUNT(ah.id) as alert_triggers
                    FROM users u
                    LEFT JOIN alerts a ON u.id = a.user_id
                    LEFT JOIN alert_history ah ON a.id = ah.alert_id
                    GROUP BY u.id, u.username, u.email, u.full_name, u.created_at
                """)
                users = self.cursor.fetchall()
                
            else:
                # PostgreSQL queries
                self.cursor.execute("""
                    SELECT 
                        u.id, u.username, u.email, u.full_name, u.created_at,
                        COUNT(a.id) as total_alerts,
                        COUNT(CASE WHEN a.is_active = true THEN 1 END) as active_alerts,
                        COUNT(ah.id) as alert_triggers
                    FROM users u
                    LEFT JOIN alerts a ON u.id = a.user_id
                    LEFT JOIN alert_history ah ON a.id = ah.alert_id
                    GROUP BY u.id, u.username, u.email, u.full_name, u.created_at
                """)
                users = self.cursor.fetchall()
            
            return {
                'timestamp': datetime.utcnow(),
                'user_analytics': [dict(user) for user in users]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_match_analytics(self) -> Dict[str, Any]:
        """Get comprehensive match analytics"""
        try:
            if self.db_type == "sqlite":
                self.cursor.execute("""
                    SELECT 
                        m.id, m.home_team, m.away_team, m.league, m.status,
                        m.home_score, m.away_score, m.start_time,
                        COUNT(a.id) as alerts_monitoring
                    FROM matches m
                    LEFT JOIN alerts a ON (a.team = m.home_team OR a.team = m.away_team)
                    GROUP BY m.id, m.home_team, m.away_team, m.league, m.status, 
                             m.home_score, m.away_score, m.start_time
                    ORDER BY m.start_time DESC
                """)
                matches = self.cursor.fetchall()
                
            else:
                self.cursor.execute("""
                    SELECT 
                        m.id, m.home_team, m.away_team, m.league, m.status,
                        m.home_score, m.away_score, m.start_time,
                        COUNT(a.id) as alerts_monitoring
                    FROM matches m
                    LEFT JOIN alerts a ON (a.team = m.home_team OR a.team = m.away_team)
                    GROUP BY m.id, m.home_team, m.away_team, m.league, m.status, 
                             m.home_score, m.away_score, m.start_time
                    ORDER BY m.start_time DESC
                """)
                matches = self.cursor.fetchall()
            
            return {
                'timestamp': datetime.utcnow(),
                'match_analytics': [dict(match) for match in matches]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_alert_analytics(self) -> Dict[str, Any]:
        """Get comprehensive alert analytics"""
        try:
            if self.db_type == "sqlite":
                self.cursor.execute("""
                    SELECT 
                        a.id, a.name, a.alert_type, a.team, a.condition,
                        a.threshold, a.is_active, a.created_at,
                        COUNT(ah.id) as trigger_count,
                        MAX(ah.triggered_at) as last_triggered
                    FROM alerts a
                    LEFT JOIN alert_history ah ON a.id = ah.alert_id
                    GROUP BY a.id, a.name, a.alert_type, a.team, a.condition,
                             a.threshold, a.is_active, a.created_at
                    ORDER BY a.created_at DESC
                """)
                alerts = self.cursor.fetchall()
                
            else:
                self.cursor.execute("""
                    SELECT 
                        a.id, a.name, a.alert_type, a.team, a.condition,
                        a.threshold, a.is_active, a.created_at,
                        COUNT(ah.id) as trigger_count,
                        MAX(ah.triggered_at) as last_triggered
                    FROM alerts a
                    LEFT JOIN alert_history ah ON a.id = ah.alert_id
                    GROUP BY a.id, a.name, a.alert_type, a.team, a.condition,
                             a.threshold, a.is_active, a.created_at
                    ORDER BY a.created_at DESC
                """)
                alerts = self.cursor.fetchall()
            
            return {
                'timestamp': datetime.utcnow(),
                'alert_analytics': [dict(alert) for alert in alerts]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = {
                'timestamp': datetime.utcnow(),
                'database_type': self.db_type,
                'tables': {},
                'summary': {}
            }
            
            if self.db_type == "sqlite":
                # Get table counts
                tables = ['users', 'matches', 'alerts', 'alert_history']
                for table in tables:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = self.cursor.fetchone()[0]
                    stats['tables'][table] = count
                
                # Get summary stats
                self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                active_users = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_active = 1")
                active_alerts = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM matches WHERE status = 'live'")
                live_matches = self.cursor.fetchone()[0]
                
            else:
                # PostgreSQL queries
                self.cursor.execute("""
                    SELECT 
                        schemaname, tablename, n_live_tup as rows
                    FROM pg_stat_user_tables
                    ORDER BY tablename
                """)
                table_stats = self.cursor.fetchall()
                
                for stat in table_stats:
                    stats['tables'][stat['tablename']] = stat['rows']
                
                # Get summary stats
                self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = true")
                active_users = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_active = true")
                active_alerts = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM matches WHERE status = 'live'")
                live_matches = self.cursor.fetchone()[0]
            
            stats['summary'] = {
                'active_users': active_users,
                'active_alerts': active_alerts,
                'live_matches': live_matches,
                'total_users': stats['tables'].get('users', 0),
                'total_matches': stats['tables'].get('matches', 0),
                'total_alerts': stats['tables'].get('alerts', 0),
                'total_alert_triggers': stats['tables'].get('alert_history', 0)
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def run_custom_query(self, query: str) -> Dict[str, Any]:
        """Run a custom SQL query"""
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            return {
                'timestamp': datetime.utcnow(),
                'query': query,
                'results': [dict(row) for row in results],
                'row_count': len(results)
            }
            
        except Exception as e:
            return {'error': str(e), 'query': query}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("TouchLine Database Query Interface")
        print("Usage: python query_db.py <command> [db_type] [args]")
        print("\nCommands:")
        print("  user-analytics [sqlite|postgres]  - Get user analytics")
        print("  match-analytics [sqlite|postgres] - Get match analytics")
        print("  alert-analytics [sqlite|postgres] - Get alert analytics")
        print("  system-stats [sqlite|postgres]    - Get system statistics")
        print("  custom-query [sqlite|postgres]    - Run custom query")
        return
    
    command = sys.argv[1]
    db_type = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ['sqlite', 'postgres'] else 'sqlite'
    
    querier = DatabaseQuerier(db_type)
    
    try:
        if command == "user-analytics":
            results = querier.get_user_analytics()
            print("👥 User Analytics:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "match-analytics":
            results = querier.get_match_analytics()
            print("⚽ Match Analytics:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "alert-analytics":
            results = querier.get_alert_analytics()
            print("🔔 Alert Analytics:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "system-stats":
            results = querier.get_system_stats()
            print("📊 System Statistics:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "custom-query":
            if len(sys.argv) < 4:
                print("Please provide a SQL query")
                return
            query = " ".join(sys.argv[3:])
            results = querier.run_custom_query(query)
            print("🔍 Custom Query Results:")
            print(json.dumps(results, indent=2, default=str))
        
        else:
            print(f"Unknown command: {command}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        querier.close()

if __name__ == "__main__":
    main()
