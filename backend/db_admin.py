#!/usr/bin/env python3
"""
TouchLine Database Administrator
Advanced database management and maintenance tools
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.database import get_db, IS_POSTGRES
from app.services.data_retention import retention_service
from app.services.scheduler import scheduler_service
from app.models import User, Match, Alert, AlertHistory, MatchCache, MatchMetrics, PlayerStats

class DatabaseAdmin:
    """Advanced database administration tools"""
    
    def __init__(self):
        self.db = next(get_db())
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        info = {
            'database_type': 'PostgreSQL' if IS_POSTGRES else 'SQLite',
            'timestamp': datetime.utcnow(),
            'tables': {},
            'indexes': {},
            'performance': {}
        }
        
        try:
            # Get table information
            if IS_POSTGRES:
                # PostgreSQL specific queries
                self.db.execute("""
                    SELECT schemaname, tablename, n_tup_ins as inserts, 
                           n_tup_upd as updates, n_tup_del as deletes,
                           n_live_tup as live_rows, n_dead_tup as dead_rows
                    FROM pg_stat_user_tables
                    ORDER BY tablename
                """)
                table_stats = self.db.fetchall()
                
                for stat in table_stats:
                    info['tables'][stat[1]] = {
                        'inserts': stat[2],
                        'updates': stat[3], 
                        'deletes': stat[4],
                        'live_rows': stat[5],
                        'dead_rows': stat[6]
                    }
            else:
                # SQLite specific queries
                tables = ['users', 'matches', 'alerts', 'alert_history', 'match_cache', 'match_metrics', 'player_stats']
                for table in tables:
                    try:
                        self.db.execute(f"SELECT COUNT(*) FROM {table}")
                        count = self.db.fetchone()[0]
                        info['tables'][table] = {'rows': count}
                    except:
                        info['tables'][table] = {'rows': 0}
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    async def run_maintenance(self) -> Dict[str, Any]:
        """Run comprehensive database maintenance"""
        print("🔧 Starting database maintenance...")
        
        results = {
            'timestamp': datetime.utcnow(),
            'maintenance_tasks': {},
            'errors': []
        }
        
        try:
            # 1. Data retention cleanup
            print("🧹 Running data retention cleanup...")
            cleanup_results = await retention_service.run_cleanup()
            results['maintenance_tasks']['data_cleanup'] = cleanup_results
            
            # 2. Database optimization
            print("⚡ Running database optimization...")
            if IS_POSTGRES:
                # PostgreSQL optimization
                self.db.execute("VACUUM ANALYZE")
                results['maintenance_tasks']['optimization'] = "VACUUM ANALYZE completed"
            else:
                # SQLite optimization
                self.db.execute("VACUUM")
                self.db.execute("ANALYZE")
                results['maintenance_tasks']['optimization'] = "VACUUM ANALYZE completed"
            
            # 3. Index analysis
            print("📊 Analyzing indexes...")
            results['maintenance_tasks']['index_analysis'] = await self._analyze_indexes()
            
            # 4. Performance analysis
            print("📈 Analyzing performance...")
            results['maintenance_tasks']['performance_analysis'] = await self._analyze_performance()
            
            self.db.commit()
            print("✅ Database maintenance completed successfully!")
            
        except Exception as e:
            print(f"❌ Database maintenance failed: {e}")
            results['errors'].append(str(e))
            self.db.rollback()
        
        return results
    
    async def _analyze_indexes(self) -> Dict[str, Any]:
        """Analyze database indexes"""
        try:
            if IS_POSTGRES:
                # PostgreSQL index analysis
                self.db.execute("""
                    SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes
                    ORDER BY idx_scan DESC
                """)
                indexes = self.db.fetchall()
                
                return {
                    'total_indexes': len(indexes),
                    'most_used': indexes[:5] if indexes else [],
                    'unused_indexes': [idx for idx in indexes if idx[3] == 0]
                }
            else:
                # SQLite index analysis
                self.db.execute("SELECT name FROM sqlite_master WHERE type='index'")
                indexes = self.db.fetchall()
                return {'total_indexes': len(indexes)}
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze database performance"""
        try:
            if IS_POSTGRES:
                # PostgreSQL performance analysis
                self.db.execute("""
                    SELECT datname, numbackends, xact_commit, xact_rollback,
                           blks_read, blks_hit, tup_returned, tup_fetched, tup_inserted,
                           tup_updated, tup_deleted
                    FROM pg_stat_database
                    WHERE datname = current_database()
                """)
                stats = self.db.fetchone()
                
                return {
                    'active_connections': stats[1] if stats else 0,
                    'commits': stats[2] if stats else 0,
                    'rollbacks': stats[3] if stats else 0,
                    'cache_hit_ratio': (stats[5] / (stats[4] + stats[5])) * 100 if stats and (stats[4] + stats[5]) > 0 else 0
                }
            else:
                # SQLite performance analysis
                return {
                    'database_size': 'N/A',
                    'cache_hit_ratio': 'N/A'
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def export_database(self, format: str = 'json') -> Dict[str, Any]:
        """Export entire database"""
        print(f"📤 Exporting database in {format} format...")
        
        try:
            export_data = {
                'export_timestamp': datetime.utcnow(),
                'database_type': 'PostgreSQL' if IS_POSTGRES else 'SQLite',
                'tables': {}
            }
            
            # Export all tables
            tables = ['users', 'matches', 'alerts', 'alert_history', 'match_cache', 'match_metrics', 'player_stats']
            
            for table in tables:
                try:
                    self.db.execute(f"SELECT * FROM {table}")
                    rows = self.db.fetchall()
                    export_data['tables'][table] = [dict(row) for row in rows]
                except Exception as e:
                    export_data['tables'][table] = {'error': str(e)}
            
            if format == 'json':
                return export_data
            else:
                return {'error': f'Unsupported format: {format}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """Close database connection"""
        self.db.close()

async def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("TouchLine Database Administrator")
        print("Usage: python db_admin.py <command> [args]")
        print("\nCommands:")
        print("  info                    - Show database information")
        print("  maintenance            - Run database maintenance")
        print("  cleanup                - Run data retention cleanup")
        print("  export [format]        - Export database")
        print("  scheduler-status       - Show scheduler status")
        print("  start-scheduler        - Start background scheduler")
        print("  stop-scheduler         - Stop background scheduler")
        return
    
    command = sys.argv[1]
    admin = DatabaseAdmin()
    
    try:
        if command == "info":
            info = admin.get_database_info()
            print("📊 Database Information:")
            print(json.dumps(info, indent=2, default=str))
        
        elif command == "maintenance":
            results = await admin.run_maintenance()
            print("🔧 Maintenance Results:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "cleanup":
            results = await retention_service.run_cleanup()
            print("🧹 Cleanup Results:")
            print(json.dumps(results, indent=2, default=str))
        
        elif command == "export":
            format_type = sys.argv[2] if len(sys.argv) > 2 else 'json'
            data = admin.export_database(format_type)
            print(json.dumps(data, indent=2, default=str))
        
        elif command == "scheduler-status":
            status = await scheduler_service.get_scheduler_status()
            print("🕐 Scheduler Status:")
            print(json.dumps(status, indent=2, default=str))
        
        elif command == "start-scheduler":
            await scheduler_service.start_scheduler()
            print("✅ Scheduler started")
        
        elif command == "stop-scheduler":
            await scheduler_service.stop_scheduler()
            print("✅ Scheduler stopped")
        
        else:
            print(f"Unknown command: {command}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        admin.close()

if __name__ == "__main__":
    asyncio.run(main())
