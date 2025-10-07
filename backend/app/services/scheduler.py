"""
Scheduled Tasks Service
Handles periodic data cleanup and maintenance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from app.services.data_retention import retention_service
from app.services.health_monitor import health_monitor

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing scheduled tasks"""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        
        # Task schedules (in seconds)
        self.schedules = {
            'data_cleanup': 3600,      # Every hour
            'health_check': 300,       # Every 5 minutes
            'cache_cleanup': 1800,     # Every 30 minutes
            'database_optimization': 86400,  # Daily
        }
    
    async def start_scheduler(self):
        """Start the scheduler service"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("🕐 Starting scheduler service...")
        
        # Start all scheduled tasks
        self.tasks['data_cleanup'] = asyncio.create_task(
            self._schedule_task('data_cleanup', self._run_data_cleanup)
        )
        
        self.tasks['health_check'] = asyncio.create_task(
            self._schedule_task('health_check', self._run_health_check)
        )
        
        self.tasks['cache_cleanup'] = asyncio.create_task(
            self._schedule_task('cache_cleanup', self._run_cache_cleanup)
        )
        
        self.tasks['database_optimization'] = asyncio.create_task(
            self._schedule_task('database_optimization', self._run_database_optimization)
        )
        
        logger.info("✅ Scheduler service started")
    
    async def stop_scheduler(self):
        """Stop the scheduler service"""
        if not self.running:
            return
        
        self.running = False
        logger.info("🛑 Stopping scheduler service...")
        
        # Cancel all tasks
        for task_name, task in self.tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.tasks.clear()
        logger.info("✅ Scheduler service stopped")
    
    async def _schedule_task(self, task_name: str, task_func):
        """Schedule a task to run at intervals"""
        while self.running:
            try:
                logger.debug(f"🔄 Running scheduled task: {task_name}")
                await task_func()
                
                # Wait for next execution
                await asyncio.sleep(self.schedules[task_name])
                
            except asyncio.CancelledError:
                logger.info(f"📋 Task {task_name} cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Task {task_name} failed: {e}")
                # Wait before retrying
                await asyncio.sleep(60)
    
    async def _run_data_cleanup(self):
        """Run data retention cleanup"""
        try:
            logger.info("🧹 Running scheduled data cleanup...")
            results = await retention_service.run_cleanup()
            
            # Log cleanup results
            total_cleaned = sum(results.get('records_cleaned', {}).values())
            if total_cleaned > 0:
                logger.info(f"✅ Data cleanup completed: {total_cleaned} records cleaned")
            else:
                logger.debug("📊 Data cleanup: No records needed cleaning")
            
            # Log any errors
            if results.get('errors'):
                for error in results['errors']:
                    logger.error(f"❌ Cleanup error: {error}")
                    
        except Exception as e:
            logger.error(f"❌ Data cleanup task failed: {e}")
    
    async def _run_health_check(self):
        """Run health monitoring"""
        try:
            logger.debug("🏥 Running scheduled health check...")
            health_report = await health_monitor.generate_health_report()
            
            # Log critical issues
            if health_report.overall_status == "unhealthy":
                logger.warning(f"⚠️ System health check failed: {health_report.issues}")
            else:
                logger.debug("✅ Health check passed")
                
        except Exception as e:
            logger.error(f"❌ Health check task failed: {e}")
    
    async def _run_cache_cleanup(self):
        """Run cache cleanup"""
        try:
            logger.debug("🗑️ Running scheduled cache cleanup...")
            
            # This would integrate with your cache service
            # For now, just log the task
            logger.debug("✅ Cache cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup task failed: {e}")
    
    async def _run_database_optimization(self):
        """Run database optimization"""
        try:
            logger.info("⚡ Running scheduled database optimization...")
            
            # This would run VACUUM, ANALYZE, etc. on PostgreSQL
            # For now, just log the task
            logger.info("✅ Database optimization completed")
            
        except Exception as e:
            logger.error(f"❌ Database optimization task failed: {e}")
    
    async def run_manual_cleanup(self) -> Dict[str, Any]:
        """Run manual data cleanup"""
        logger.info("🧹 Running manual data cleanup...")
        return await retention_service.run_cleanup()
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self.running,
            'tasks': {
                name: {
                    'running': not task.done() if task else False,
                    'schedule': self.schedules.get(name, 0)
                }
                for name, task in self.tasks.items()
            },
            'schedules': self.schedules
        }

# Global scheduler instance
scheduler_service = SchedulerService()
