"""
Database Admin API Routes
Web-based database query interface
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
import json
from datetime import datetime
from app.database import get_db, IS_POSTGRES

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get comprehensive database statistics"""
    try:
        stats = {
            'timestamp': datetime.utcnow(),
            'database_type': 'PostgreSQL' if IS_POSTGRES else 'SQLite',
            'tables': {},
            'summary': {}
        }
        
        if IS_POSTGRES:
            # PostgreSQL queries
            result = db.execute(text("""
                SELECT 
                    schemaname, tablename, n_live_tup as rows
                FROM pg_stat_user_tables
                ORDER BY tablename
            """))
            table_stats = result.fetchall()
            
            for stat in table_stats:
                stats['tables'][stat.tablename] = stat.rows
            
            # Get summary stats
            result = db.execute(text("SELECT COUNT(*) FROM users WHERE is_active = true"))
            active_users = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM alerts WHERE is_active = true"))
            active_alerts = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM matches WHERE status = 'live'"))
            live_matches = result.scalar()
            
        else:
            # SQLite queries
            tables = ['users', 'matches', 'alerts', 'alert_history']
            for table in tables:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                stats['tables'][table] = count
            
            result = db.execute(text("SELECT COUNT(*) FROM users WHERE is_active = 1"))
            active_users = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM alerts WHERE is_active = 1"))
            active_alerts = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM matches WHERE status = 'live'"))
            live_matches = result.scalar()
        
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/users")
async def get_users_analytics(db: Session = Depends(get_db)):
    """Get user analytics with alert counts"""
    try:
        if IS_POSTGRES:
            result = db.execute(text("""
                SELECT 
                    u.id, u.username, u.email, u.full_name, u.created_at,
                    COUNT(a.id) as total_alerts,
                    COUNT(CASE WHEN a.is_active = true THEN 1 END) as active_alerts,
                    COUNT(ah.id) as alert_triggers
                FROM users u
                LEFT JOIN alerts a ON u.id = a.user_id
                LEFT JOIN alert_history ah ON a.id = ah.alert_id
                GROUP BY u.id, u.username, u.email, u.full_name, u.created_at
            """))
        else:
            result = db.execute(text("""
                SELECT 
                    u.id, u.username, u.email, u.full_name, u.created_at,
                    COUNT(a.id) as total_alerts,
                    COUNT(CASE WHEN a.is_active = 1 THEN 1 END) as active_alerts,
                    COUNT(ah.id) as alert_triggers
                FROM users u
                LEFT JOIN alerts a ON u.id = a.user_id
                LEFT JOIN alert_history ah ON a.id = ah.alert_id
                GROUP BY u.id, u.username, u.email, u.full_name, u.created_at
            """))
        
        users = result.fetchall()
        return {
            'timestamp': datetime.utcnow(),
            'users': [dict(user._mapping) for user in users]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/matches")
async def get_matches_analytics(db: Session = Depends(get_db)):
    """Get match analytics with alert monitoring"""
    try:
        result = db.execute(text("""
            SELECT 
                m.id, m.home_team, m.away_team, m.league, m.status,
                m.home_score, m.away_score, m.start_time,
                COUNT(a.id) as alerts_monitoring
            FROM matches m
            LEFT JOIN alerts a ON (a.team = m.home_team OR a.team = m.away_team)
            GROUP BY m.id, m.home_team, m.away_team, m.league, m.status, 
                     m.home_score, m.away_score, m.start_time
            ORDER BY m.start_time DESC
        """))
        
        matches = result.fetchall()
        return {
            'timestamp': datetime.utcnow(),
            'matches': [dict(match._mapping) for match in matches]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/alerts")
async def get_alerts_analytics(db: Session = Depends(get_db)):
    """Get alert analytics with trigger history"""
    try:
        if IS_POSTGRES:
            result = db.execute(text("""
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
            """))
        else:
            result = db.execute(text("""
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
            """))
        
        alerts = result.fetchall()
        return {
            'timestamp': datetime.utcnow(),
            'alerts': [dict(alert._mapping) for alert in alerts]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/query")
async def execute_custom_query(
    query: str,
    db: Session = Depends(get_db)
):
    """Execute custom SQL query (admin only)"""
    try:
        # Security: Only allow SELECT queries
        if not query.strip().upper().startswith('SELECT'):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        result = db.execute(text(query))
        rows = result.fetchall()
        
        return {
            'timestamp': datetime.utcnow(),
            'query': query,
            'results': [dict(row._mapping) for row in rows],
            'row_count': len(rows)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/export")
async def export_database(db: Session = Depends(get_db)):
    """Export all database data"""
    try:
        export_data = {
            'export_timestamp': datetime.utcnow(),
            'database_type': 'PostgreSQL' if IS_POSTGRES else 'SQLite',
            'tables': {}
        }
        
        tables = ['users', 'matches', 'alerts', 'alert_history']
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                export_data['tables'][table] = [dict(row._mapping) for row in rows]
            except Exception as e:
                export_data['tables'][table] = {'error': str(e)}
        
        return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
