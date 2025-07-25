import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from .data_service import data_service

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks for the application"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def start_background_tasks(self):
        """Start all background tasks"""
        self.running = True
        logger.info("🚀 Starting background tasks...")
        
        # Start cache cleanup task
        cache_cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        self.tasks.append(cache_cleanup_task)
        
        logger.info("✅ Background tasks started")
    
    async def stop_background_tasks(self):
        """Stop all background tasks"""
        self.running = False
        logger.info("🛑 Stopping background tasks...")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("✅ Background tasks stopped")
    
    async def _cache_cleanup_loop(self):
        """Periodically clean up expired cache entries"""
        while self.running:
            try:
                await data_service.cleanup_expired_cache()
                logger.info("🧹 Cache cleanup completed")
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}")
            
            # Wait 10 minutes before next cleanup
            await asyncio.sleep(600)
    
    async def cleanup_old_metrics(self, days: int = 7):
        """Clean up old metrics data"""
        try:
            from .database import get_db
            from .models import MatchMetrics
            
            db = next(get_db())
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                deleted_count = db.query(MatchMetrics).filter(
                    MatchMetrics.timestamp < cutoff_date
                ).delete()
                
                db.commit()
                logger.info(f"🧹 Cleaned up {deleted_count} old metrics entries")
                
            except Exception as e:
                logger.error(f"Error cleaning up old metrics: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in cleanup_old_metrics: {e}")

# Global instance
background_task_manager = BackgroundTaskManager() 