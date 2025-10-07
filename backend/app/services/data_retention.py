"""
Data Retention and Cleanup Service
Manages automatic data cleanup and retention policies
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.database import get_db
from app.models import Match, MatchCache, MatchMetrics, AlertHistory, PlayerStats

logger = logging.getLogger(__name__)

class DataRetentionService:
    """Service for managing data retention and cleanup policies"""
    
    def __init__(self):
        # Retention policies (in days)
        self.retention_policies = {
            'match_cache': 7,      # Keep match cache for 7 days
            'match_metrics': 30,   # Keep match metrics for 30 days
            'alert_history': 90,   # Keep alert history for 90 days
            'player_stats': 30,    # Keep player stats for 30 days
            'old_matches': 365,    # Keep match records for 1 year
            'inactive_users': 180,  # Mark inactive users after 6 months
        }
        
        # Cleanup thresholds
        self.cleanup_thresholds = {
            'max_cache_entries': 10000,    # Max cache entries
            'max_alert_history': 50000,    # Max alert history entries
            'max_player_stats': 100000,   # Max player stats entries
        }
    
    async def run_cleanup(self) -> Dict[str, Any]:
        """Run comprehensive data cleanup"""
        logger.info("🧹 Starting data retention cleanup...")
        
        cleanup_results = {
            'timestamp': datetime.utcnow(),
            'policies_applied': {},
            'records_cleaned': {},
            'errors': []
        }
        
        db = next(get_db())
        try:
            # 1. Clean expired match cache
            await self._cleanup_match_cache(db, cleanup_results)
            
            # 2. Clean old match metrics
            await self._cleanup_match_metrics(db, cleanup_results)
            
            # 3. Clean old alert history
            await self._cleanup_alert_history(db, cleanup_results)
            
            # 4. Clean old player stats
            await self._cleanup_player_stats(db, cleanup_results)
            
            # 5. Clean old matches
            await self._cleanup_old_matches(db, cleanup_results)
            
            # 6. Optimize database
            await self._optimize_database(db, cleanup_results)
            
            db.commit()
            logger.info("✅ Data retention cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Data retention cleanup failed: {e}")
            cleanup_results['errors'].append(str(e))
            db.rollback()
        finally:
            db.close()
        
        return cleanup_results
    
    async def _cleanup_match_cache(self, db: Session, results: Dict[str, Any]):
        """Clean expired match cache entries"""
        try:
            # Delete expired cache entries
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_policies['match_cache'])
            
            expired_count = db.query(MatchCache).filter(
                MatchCache.last_updated < cutoff_date
            ).delete()
            
            # Limit total cache entries
            total_cache = db.query(MatchCache).count()
            if total_cache > self.cleanup_thresholds['max_cache_entries']:
                excess_count = total_cache - self.cleanup_thresholds['max_cache_entries']
                oldest_entries = db.query(MatchCache).order_by(
                    MatchCache.last_updated.asc()
                ).limit(excess_count).all()
                
                for entry in oldest_entries:
                    db.delete(entry)
                
                expired_count += excess_count
            
            results['records_cleaned']['match_cache'] = expired_count
            results['policies_applied']['match_cache'] = f"Deleted {expired_count} expired cache entries"
            
        except Exception as e:
            logger.error(f"Error cleaning match cache: {e}")
            results['errors'].append(f"Match cache cleanup: {e}")
    
    async def _cleanup_match_metrics(self, db: Session, results: Dict[str, Any]):
        """Clean old match metrics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_policies['match_metrics'])
            
            deleted_count = db.query(MatchMetrics).filter(
                MatchMetrics.timestamp < cutoff_date
            ).delete()
            
            results['records_cleaned']['match_metrics'] = deleted_count
            results['policies_applied']['match_metrics'] = f"Deleted {deleted_count} old metrics"
            
        except Exception as e:
            logger.error(f"Error cleaning match metrics: {e}")
            results['errors'].append(f"Match metrics cleanup: {e}")
    
    async def _cleanup_alert_history(self, db: Session, results: Dict[str, Any]):
        """Clean old alert history"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_policies['alert_history'])
            
            # Delete old alert history
            deleted_count = db.query(AlertHistory).filter(
                AlertHistory.triggered_at < cutoff_date
            ).delete()
            
            # Limit total alert history
            total_history = db.query(AlertHistory).count()
            if total_history > self.cleanup_thresholds['max_alert_history']:
                excess_count = total_history - self.cleanup_thresholds['max_alert_history']
                oldest_entries = db.query(AlertHistory).order_by(
                    AlertHistory.triggered_at.asc()
                ).limit(excess_count).all()
                
                for entry in oldest_entries:
                    db.delete(entry)
                
                deleted_count += excess_count
            
            results['records_cleaned']['alert_history'] = deleted_count
            results['policies_applied']['alert_history'] = f"Deleted {deleted_count} old alert history"
            
        except Exception as e:
            logger.error(f"Error cleaning alert history: {e}")
            results['errors'].append(f"Alert history cleanup: {e}")
    
    async def _cleanup_player_stats(self, db: Session, results: Dict[str, Any]):
        """Clean old player stats"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_policies['player_stats'])
            
            deleted_count = db.query(PlayerStats).filter(
                PlayerStats.timestamp < cutoff_date
            ).delete()
            
            results['records_cleaned']['player_stats'] = deleted_count
            results['policies_applied']['player_stats'] = f"Deleted {deleted_count} old player stats"
            
        except Exception as e:
            logger.error(f"Error cleaning player stats: {e}")
            results['errors'].append(f"Player stats cleanup: {e}")
    
    async def _cleanup_old_matches(self, db: Session, results: Dict[str, Any]):
        """Clean very old match records"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_policies['old_matches'])
            
            # Only delete matches that are finished and very old
            deleted_count = db.query(Match).filter(
                Match.status == 'finished',
                Match.created_at < cutoff_date
            ).delete()
            
            results['records_cleaned']['old_matches'] = deleted_count
            results['policies_applied']['old_matches'] = f"Deleted {deleted_count} old finished matches"
            
        except Exception as e:
            logger.error(f"Error cleaning old matches: {e}")
            results['errors'].append(f"Old matches cleanup: {e}")
    
    async def _optimize_database(self, db: Session, results: Dict[str, Any]):
        """Optimize database performance"""
        try:
            # Get current database stats
            stats = {
                'match_cache_count': db.query(MatchCache).count(),
                'match_metrics_count': db.query(MatchMetrics).count(),
                'alert_history_count': db.query(AlertHistory).count(),
                'player_stats_count': db.query(PlayerStats).count(),
                'matches_count': db.query(Match).count(),
            }
            
            results['database_stats'] = stats
            results['policies_applied']['optimization'] = "Database stats collected"
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            results['errors'].append(f"Database optimization: {e}")
    
    async def get_retention_report(self) -> Dict[str, Any]:
        """Generate data retention report"""
        db = next(get_db())
        try:
            report = {
                'timestamp': datetime.utcnow(),
                'retention_policies': self.retention_policies,
                'cleanup_thresholds': self.cleanup_thresholds,
                'current_counts': {},
                'recommendations': []
            }
            
            # Get current record counts
            report['current_counts'] = {
                'match_cache': db.query(MatchCache).count(),
                'match_metrics': db.query(MatchMetrics).count(),
                'alert_history': db.query(AlertHistory).count(),
                'player_stats': db.query(PlayerStats).count(),
                'matches': db.query(Match).count(),
            }
            
            # Generate recommendations
            if report['current_counts']['match_cache'] > self.cleanup_thresholds['max_cache_entries']:
                report['recommendations'].append("Match cache is over threshold - run cleanup")
            
            if report['current_counts']['alert_history'] > self.cleanup_thresholds['max_alert_history']:
                report['recommendations'].append("Alert history is over threshold - run cleanup")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating retention report: {e}")
            return {'error': str(e)}
        finally:
            db.close()

# Global instance
retention_service = DataRetentionService()
