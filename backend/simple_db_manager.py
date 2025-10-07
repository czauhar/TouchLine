#!/usr/bin/env python3
"""
Simple Database Manager
Direct database access without app dependencies
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

class SimpleDBManager:
    """Simple database manager for direct access"""
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'database_type': self.db_type,
            'timestamp': datetime.utcnow(),
            'tables': {}
        }
        
        try:
            if self.db_type == "sqlite":
                # Get SQLite table info
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in self.cursor.fetchall()]
                
                for table in tables:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = self.cursor.fetchone()[0]
                    stats['tables'][table] = {'rows': count}
            
            elif self.db_type == "postgres":
                # Get PostgreSQL table info
                self.cursor.execute("""
                    SELECT schemaname, tablename, n_live_tup as rows
                    FROM pg_stat_user_tables
                    ORDER BY tablename
                """)
                table_stats = self.cursor.fetchall()
                
                for stat in table_stats:
                    stats['tables'][stat['tablename']] = {'rows': stat['rows']}
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old data"""
        results = {
            'timestamp': datetime.utcnow(),
            'days_cleaned': days,
            'records_deleted': {},
            'errors': []
        }
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            if self.db_type == "sqlite":
                # Clean SQLite data
                tables_to_clean = [
                    ('match_cache', 'last_updated'),
                    ('alert_history', 'triggered_at'),
                    ('player_stats', 'timestamp')
                ]
                
                for table, date_column in tables_to_clean:
                    try:
                        self.cursor.execute(f"""
                            DELETE FROM {table} 
                            WHERE {date_column} < ?
                        """, (cutoff_date,))
                        deleted = self.cursor.rowcount
                        results['records_deleted'][table] = deleted
                    except Exception as e:
                        results['errors'].append(f"Error cleaning {table}: {e}")
            
            elif self.db_type == "postgres":
                # Clean PostgreSQL data
                self.cursor.execute("""
                    DELETE FROM match_cache 
                    WHERE last_updated < %s
                """, (cutoff_date,))
                results['records_deleted']['match_cache'] = self.cursor.rowcount
                
                self.cursor.execute("""
                    DELETE FROM alert_history 
                    WHERE triggered_at < %s
                """, (cutoff_date,))
                results['records_deleted']['alert_history'] = self.cursor.rowcount
                
                self.cursor.execute("""
                    DELETE FROM player_stats 
                    WHERE timestamp < %s
                """, (cutoff_date,))
                results['records_deleted']['player_stats'] = self.cursor.rowcount
            
            self.conn.commit()
            return results
            
        except Exception as e:
            results['errors'].append(str(e))
            self.conn.rollback()
            return results
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance"""
        results = {
            'timestamp': datetime.utcnow(),
            'optimizations': [],
            'errors': []
        }
        
        try:
            if self.db_type == "sqlite":
                # SQLite optimization
                self.cursor.execute("VACUUM")
                results['optimizations'].append("VACUUM completed")
                
                self.cursor.execute("ANALYZE")
                results['optimizations'].append("ANALYZE completed")
            
            elif self.db_type == "postgres":
                # PostgreSQL optimization
                self.cursor.execute("VACUUM ANALYZE")
                results['optimizations'].append("VACUUM ANALYZE completed")
            
            self.conn.commit()
            return results
            
        except Exception as e:
            results['errors'].append(str(e))
            return results
    
    def export_data(self, table: str = None) -> Dict[str, Any]:
        """Export data to JSON"""
        try:
            if table:
                # Export specific table
                self.cursor.execute(f"SELECT * FROM {table}")
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                # Export all tables
                if self.db_type == "sqlite":
                    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in self.cursor.fetchall()]
                elif self.db_type == "postgres":
                    self.cursor.execute("""
                        SELECT tablename FROM pg_tables 
                        WHERE schemaname = 'public'
                    """)
                    tables = [row['tablename'] for row in self.cursor.fetchall()]
                
                data = {}
                for table_name in tables:
                    try:
                        self.cursor.execute(f"SELECT * FROM {table_name}")
                        rows = self.cursor.fetchall()
                        data[table_name] = [dict(row) for row in rows]
                    except Exception as e:
                        data[table_name] = {'error': str(e)}
                
                return data
                
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Simple Database Manager")
        print("Usage: python simple_db_manager.py <command> [args]")
        print("\nCommands:")
        print("  stats [sqlite|postgres]  - Show database statistics")
        print("  cleanup [days]           - Clean old data")
        print("  optimize                 - Optimize database")
        print("  export [table]           - Export data")
        return
    
    command = sys.argv[1]
    db_type = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ['sqlite', 'postgres'] else 'sqlite'
    
    db = SimpleDBManager(db_type)
    
    try:
        if command == "stats":
            stats = db.get_stats()
            print("📊 Database Statistics:")
            print(json.dumps(stats, indent=2, default=str))
        
        elif command == "cleanup":
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            results = db.cleanup_old_data(days)
            print("🧹 Cleanup Results:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "optimize":
            results = db.optimize_database()
            print("⚡ Optimization Results:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "export":
            table = sys.argv[3] if len(sys.argv) > 3 else None
            data = db.export_data(table)
            print(json.dumps(data, indent=2, default=str))
        
        else:
            print(f"Unknown command: {command}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
