import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .sports_api import sports_api
from .sms_service import sms_service
from .database import get_db
from .models import Match, Alert, AlertHistory
from .analytics import (
    analytics_engine, MatchMetrics, AdvancedAlertCondition,
    Condition, ConditionType, Operator, LogicOperator, TimeWindow
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertType(Enum):
    GOALS = "goals"
    SCORE_DIFFERENCE = "score_difference"
    POSSESSION = "possession"
    TIME_BASED = "time_based"
    CARDS = "cards"
    XG = "xg"
    MOMENTUM = "momentum"
    PRESSURE = "pressure"
    WIN_PROBABILITY = "win_probability"
    CUSTOM = "custom"
    # Player-specific alert types
    PLAYER_GOALS = "player_goals"
    PLAYER_ASSISTS = "player_assists"
    PLAYER_CARDS = "player_cards"
    PLAYER_SHOTS = "player_shots"
    PLAYER_PASSES = "player_passes"
    PLAYER_TACKLES = "player_tackles"
    PLAYER_RATING = "player_rating"
    PLAYER_MINUTES = "player_minutes"
    PLAYER_GOAL_CONTRIBUTIONS = "player_goal_contributions"

@dataclass
class AlertCondition:
    alert_id: int
    alert_type: AlertType
    team: str
    condition: str
    threshold: float
    time_window: Optional[int] = None  # minutes
    user_phone: str = ""
    # Player-specific fields
    player_id: Optional[int] = None
    player_name: Optional[str] = None

class MatchMonitor:
    def __init__(self):
        self.running = False
        self.monitoring_interval = 60  # seconds
        self.active_matches = {}  # fixture_id -> match_data
        self.alert_conditions = {}  # alert_id -> AlertCondition
        
    async def start_monitoring(self):
        """Start the background monitoring service"""
        self.running = True
        logger.info("🚀 Starting Match Monitor...")
        
        while self.running:
            try:
                await self.monitor_live_matches()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in match monitoring: {e}")
                await asyncio.sleep(30)  # Shorter sleep on error
    
    async def stop_monitoring(self):
        """Stop the background monitoring service"""
        self.running = False
        logger.info("🛑 Stopping Match Monitor...")
    
    async def monitor_live_matches(self):
        """Monitor all live matches and evaluate alerts"""
        logger.info("📊 Monitoring live matches...")
        
        # Fetch live matches using efficient data service
        from .data_service import data_service
        live_matches_data = await data_service.get_live_matches_efficient()
        
        # Update active matches
        for match_data in live_matches_data:
            fixture_id = int(match_data.external_id)
            self.active_matches[fixture_id] = match_data
        
        # Remove finished matches
        finished_matches = []
        for fixture_id, match_data in self.active_matches.items():
            if match_data.status in ["FT", "AET", "PEN"]:  # Full Time, Extra Time, Penalties
                finished_matches.append(fixture_id)
        
        for fixture_id in finished_matches:
            del self.active_matches[fixture_id]
        
        # Load active alerts
        await self.load_active_alerts()
        
        # Evaluate alerts for each active match
        for fixture_id, match_data in self.active_matches.items():
            await self.evaluate_match_alerts(fixture_id, match_data)
    
    async def load_active_alerts(self):
        """Load all active alerts from database"""
        try:
            db = next(get_db())
            alerts = db.query(Alert).filter(Alert.is_active == True).all()
            
            # Clear existing conditions
            self.alert_conditions = {}
            
            for alert in alerts:
                if alert.alert_type == "advanced":
                    # Handle advanced alerts with JSON conditions
                    try:
                        conditions_data = json.loads(alert.condition)
                        # Create AdvancedAlertCondition object
                        advanced_condition = AdvancedAlertCondition(
                            alert_id=alert.id,
                            name=alert.name,
                            description=conditions_data.get('description', ''),
                            logic_operator=LogicOperator(conditions_data.get('logic_operator', 'AND')),
                            user_phone=alert.user_phone or conditions_data.get('user_phone', '')
                        )
                        
                        # Add conditions
                        for cond_data in conditions_data.get('conditions', []):
                            condition = Condition(
                                condition_type=ConditionType(cond_data.get('type', 'goals')),
                                team=cond_data.get('team', ''),
                                operator=Operator(cond_data.get('operator', '>=')),
                                value=cond_data.get('value', 0),
                                description=cond_data.get('description', '')
                            )
                            advanced_condition.add_condition(condition)
                        
                        # Add time windows
                        for window_data in conditions_data.get('time_windows', []):
                            time_window = TimeWindow(
                                start_minute=window_data.get('start_minute', 0),
                                end_minute=window_data.get('end_minute', 90),
                                description=window_data.get('description', '')
                            )
                            advanced_condition.add_time_window(time_window)
                        
                        # Store the advanced condition
                        self.alert_conditions[alert.id] = advanced_condition
                        
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in advanced alert {alert.id}")
                        continue
                else:
                    # Handle simple alerts
                    alert_condition = AlertCondition(
                        alert_id=alert.id,
                        alert_type=AlertType(alert.alert_type),
                        team=alert.team,
                        condition=alert.condition,
                        threshold=alert.threshold,
                        time_window=alert.time_window,
                        user_phone=alert.user_phone
                    )
                    self.alert_conditions[alert.id] = alert_condition
                
            logger.info(f"📋 Loaded {len(self.alert_conditions)} active alerts")
            
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
    
    async def evaluate_match_alerts(self, fixture_id: int, match_data):
        """Evaluate all alerts for a specific match"""
        # Handle both Dict and MatchData objects
        if hasattr(match_data, 'external_id'):  # MatchData object
            match_info = match_data
            # Create a simple metrics object for MatchData
            from .analytics import MatchMetrics
            metrics = MatchMetrics(
                home_team=match_data.home_team,
                away_team=match_data.away_team,
                home_score=match_data.home_score,
                away_score=match_data.away_score,
                home_xg=match_data.home_xg,
                away_xg=match_data.away_xg,
                home_momentum=match_data.home_momentum,
                away_momentum=match_data.away_momentum,
                home_pressure_index=match_data.home_pressure,
                away_pressure_index=match_data.away_pressure,
                home_win_probability=0.5,  # Default
                away_win_probability=0.5   # Default
            )
        else:  # Dict object
            match_info = sports_api.format_match_data(match_data)
            metrics = analytics_engine.calculate_all_metrics(match_data)
        
        for alert_id, condition in self.alert_conditions.items():
            # Check if this alert applies to this match
            if isinstance(condition, AdvancedAlertCondition):
                # Handle advanced alerts
                await self.evaluate_advanced_alert(condition, match_data, metrics)
            else:
                # Handle simple alerts
                if self.matches_alert_criteria(match_info, condition):
                    await self.evaluate_single_alert(alert_id, condition, match_info, metrics)
    
    def matches_alert_criteria(self, match_info, condition: AlertCondition) -> bool:
        """Check if a match matches the alert criteria"""
        # Handle both Dict and MatchData objects
        if hasattr(match_info, 'home_team'):  # MatchData object
            home_team = match_info.home_team.lower()
            away_team = match_info.away_team.lower()
        else:  # Dict object
            home_team = match_info.get("home_team", "").lower()
            away_team = match_info.get("away_team", "").lower()
        
        target_team = condition.team.lower()
        return target_team in home_team or target_team in away_team
    
    async def evaluate_single_alert(self, alert_id: int, condition: AlertCondition, match_info, metrics: MatchMetrics):
        """Evaluate a single alert condition"""
        try:
            # Check if alert was already triggered for this match
            external_id = match_info.external_id if hasattr(match_info, 'external_id') else match_info.get("external_id")
            if await self.alert_already_triggered(alert_id, external_id):
                return
            
            # Evaluate based on alert type
            triggered = False
            trigger_message = ""
            
            if condition.alert_type == AlertType.GOALS:
                triggered, trigger_message = self.evaluate_goals_alert(condition, match_info)
            elif condition.alert_type == AlertType.SCORE_DIFFERENCE:
                triggered, trigger_message = self.evaluate_score_difference_alert(condition, match_info)
            elif condition.alert_type == AlertType.TIME_BASED:
                triggered, trigger_message = self.evaluate_time_based_alert(condition, match_info)
            elif condition.alert_type == AlertType.XG:
                triggered, trigger_message = self.evaluate_xg_alert(condition, metrics)
            elif condition.alert_type == AlertType.MOMENTUM:
                triggered, trigger_message = self.evaluate_momentum_alert(condition, metrics)
            elif condition.alert_type == AlertType.PRESSURE:
                triggered, trigger_message = self.evaluate_pressure_alert(condition, metrics)
            elif condition.alert_type == AlertType.WIN_PROBABILITY:
                triggered, trigger_message = self.evaluate_win_probability_alert(condition, metrics)
            # Player-specific alerts
            elif condition.alert_type == AlertType.PLAYER_GOALS:
                triggered, trigger_message = self.evaluate_player_goals_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_ASSISTS:
                triggered, trigger_message = self.evaluate_player_assists_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_CARDS:
                triggered, trigger_message = self.evaluate_player_cards_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_SHOTS:
                triggered, trigger_message = self.evaluate_player_shots_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_PASSES:
                triggered, trigger_message = self.evaluate_player_passes_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_TACKLES:
                triggered, trigger_message = self.evaluate_player_tackles_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_RATING:
                triggered, trigger_message = self.evaluate_player_rating_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_MINUTES:
                triggered, trigger_message = self.evaluate_player_minutes_alert(condition, metrics)
            elif condition.alert_type == AlertType.PLAYER_GOAL_CONTRIBUTIONS:
                triggered, trigger_message = self.evaluate_player_goal_contributions_alert(condition, metrics)
            
            # Send alert if triggered
            if triggered:
                await self.send_alert(alert_id, condition, match_info, trigger_message)
                
        except Exception as e:
            logger.error(f"Error evaluating alert {alert_id}: {e}")
    
    async def evaluate_advanced_alert(self, alert_condition: AdvancedAlertCondition, match_data: Dict, metrics: MatchMetrics):
        """Evaluate an advanced alert condition with multi-condition logic"""
        try:
            # Check if alert was already triggered for this match
            match_info = sports_api.format_match_data(match_data)
            if await self.alert_already_triggered(alert_condition.alert_id, match_info.get("external_id")):
                return False, ""
            
            # Evaluate the advanced condition
            triggered, trigger_message = await analytics_engine.evaluate_advanced_condition(
                alert_condition, match_data, metrics
            )
            
            # Send alert if triggered
            if triggered:
                await self.send_alert(alert_condition.alert_id, None, match_info, trigger_message)
            
            return triggered, trigger_message
                
        except Exception as e:
            logger.error(f"Error evaluating advanced alert {alert_condition.alert_id}: {e}")
            return False, ""
    
    def evaluate_goals_alert(self, condition: AlertCondition, match_info) -> tuple[bool, str]:
        """Evaluate goals-based alert"""
        # Handle both Dict and MatchData objects
        if hasattr(match_info, 'home_team'):  # MatchData object
            home_team = match_info.home_team
            away_team = match_info.away_team
            home_score = match_info.home_score
            away_score = match_info.away_score
        else:  # Dict object
            home_team = match_info.get("home_team", "")
            away_team = match_info.get("away_team", "")
            home_score = match_info.get("home_score", 0)
            away_score = match_info.get("away_score", 0)
        
        target_team = condition.team
        team_score = home_score if target_team in home_team else away_score
        
        if team_score >= condition.threshold:
            return True, f"{target_team} has scored {team_score} goals"
        
        return False, ""
    
    def evaluate_score_difference_alert(self, condition: AlertCondition, match_info) -> tuple[bool, str]:
        """Evaluate score difference alert"""
        # Handle both Dict and MatchData objects
        if hasattr(match_info, 'home_team'):  # MatchData object
            home_team = match_info.home_team
            away_team = match_info.away_team
            home_score = match_info.home_score
            away_score = match_info.away_score
        else:  # Dict object
            home_team = match_info.get("home_team", "")
            away_team = match_info.get("away_team", "")
            home_score = match_info.get("home_score", 0)
            away_score = match_info.get("away_score", 0)
        
        target_team = condition.team
        if target_team in home_team:
            difference = home_score - away_score
        else:
            difference = away_score - home_score
        
        if difference >= condition.threshold:
            return True, f"{target_team} leads by {difference} goals"
        
        return False, ""
    
    def evaluate_time_based_alert(self, condition: AlertCondition, match_info) -> tuple[bool, str]:
        """Evaluate time-based alert"""
        # Handle both Dict and MatchData objects
        if hasattr(match_info, 'elapsed_time'):  # MatchData object
            elapsed = match_info.elapsed_time
        else:  # Dict object
            elapsed = match_info.get("elapsed", 0)
        
        if condition.time_window and elapsed >= condition.time_window:
            return True, f"Match has reached {elapsed} minutes"
        
        return False, ""
    
    def evaluate_xg_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate xG-based alert"""
        target_team = condition.team
        team_xg = metrics.home_xg if target_team.lower() in metrics.home_team.lower() else metrics.away_xg
        
        if team_xg >= condition.threshold:
            return True, f"{target_team} xG: {team_xg:.2f} >= {condition.threshold}"
        
        return False, ""
    
    def evaluate_momentum_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate momentum-based alert"""
        target_team = condition.team
        team_momentum = metrics.home_momentum if target_team.lower() in metrics.home_team.lower() else metrics.away_momentum
        
        if team_momentum >= condition.threshold:
            return True, f"{target_team} momentum: {team_momentum:.1f} >= {condition.threshold}"
        
        return False, ""
    
    def evaluate_pressure_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate pressure-based alert"""
        target_team = condition.team
        team_pressure = metrics.home_pressure_index if target_team.lower() in metrics.home_team.lower() else metrics.away_pressure_index
        
        if team_pressure >= condition.threshold:
            return True, f"{target_team} pressure: {team_pressure:.2f} >= {condition.threshold}"
        
        return False, ""
    
    def evaluate_win_probability_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate win probability alert"""
        target_team = condition.team
        team_win_prob = metrics.home_win_probability if target_team.lower() in metrics.home_team.lower() else metrics.away_win_probability
        
        if team_win_prob >= condition.threshold:
            return True, f"{target_team} win probability: {team_win_prob:.1%} >= {condition.threshold:.1%}"
        
        return False, ""
    
    # =============================================================================
    # Player-Specific Alert Evaluation Methods
    # =============================================================================
    
    def _get_player_stats(self, condition: AlertCondition, metrics: MatchMetrics):
        """Get player statistics for a condition"""
        if not condition.player_id:
            return None
        
        return metrics.players.get(condition.player_id)
    
    def evaluate_player_goals_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player goals alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.goals >= condition.threshold:
            return True, f"{player.player_name} has scored {player.goals} goals"
        
        return False, ""
    
    def evaluate_player_assists_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player assists alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.assists >= condition.threshold:
            return True, f"{player.player_name} has {player.assists} assists"
        
        return False, ""
    
    def evaluate_player_cards_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player cards alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        total_cards = player.yellow_cards + player.red_cards
        if total_cards >= condition.threshold:
            return True, f"{player.player_name} has {total_cards} cards"
        
        return False, ""
    
    def evaluate_player_shots_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player shots alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.shots >= condition.threshold:
            return True, f"{player.player_name} has {player.shots} shots"
        
        return False, ""
    
    def evaluate_player_passes_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player passes alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.passes >= condition.threshold:
            return True, f"{player.player_name} has {player.passes} passes"
        
        return False, ""
    
    def evaluate_player_tackles_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player tackles alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.tackles >= condition.threshold:
            return True, f"{player.player_name} has {player.tackles} tackles"
        
        return False, ""
    
    def evaluate_player_rating_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player rating alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.rating >= condition.threshold:
            return True, f"{player.player_name} rating: {player.rating:.2f} >= {condition.threshold}"
        
        return False, ""
    
    def evaluate_player_minutes_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player minutes alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        if player.minutes_played >= condition.threshold:
            return True, f"{player.player_name} has played {player.minutes_played} minutes"
        
        return False, ""
    
    def evaluate_player_goal_contributions_alert(self, condition: AlertCondition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate player goal contributions alert"""
        player = self._get_player_stats(condition, metrics)
        if not player:
            return False, f"Player {condition.player_name or condition.player_id} not found"
        
        contributions = player.goal_contributions
        if contributions >= condition.threshold:
            return True, f"{player.player_name} has {contributions} goal contributions"
        
        return False, ""
    
    async def alert_already_triggered(self, alert_id: int, match_id: str) -> bool:
        """Check if alert was already triggered for this match"""
        try:
            db = next(get_db())
            existing = db.query(AlertHistory).filter(
                AlertHistory.alert_id == alert_id,
                AlertHistory.match_id == match_id
            ).first()
            
            return existing is not None
            
        except Exception as e:
            logger.error(f"Error checking alert history: {e}")
            return False
    
    async def send_alert(self, alert_id: int, condition: AlertCondition, match_info: Dict, trigger_message: str):
        """Send SMS alert and record in history"""
        try:
            # Format alert message
            message = sms_service.format_alert_message(
                f"Alert #{alert_id}",
                match_info,
                trigger_message
            )
            
            # Initialize result
            result = {"success": False, "message_sid": ""}
            
            # Send SMS
            if condition and condition.user_phone:
                result = sms_service.send_alert(condition.user_phone, message)
                logger.info(f"📱 Alert {alert_id} sent: {result.get('success', False)}")
            else:
                logger.info(f"📱 Alert {alert_id} triggered (no phone number configured)")
            
            # Send WebSocket notification
            await self.send_websocket_notification(alert_id, condition, match_info, trigger_message)
            
            # Record in history
            await self.record_alert_history(alert_id, match_info, trigger_message, result)
            
        except Exception as e:
            logger.error(f"Error sending alert {alert_id}: {e}")
    
    async def send_websocket_notification(self, alert_id: int, condition: AlertCondition, match_info: Dict, trigger_message: str):
        """Send real-time WebSocket notification"""
        try:
            from .websocket_manager import websocket_manager
            
            # Get user ID from alert
            db = next(get_db())
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if alert and alert.user_id:
                alert_data = {
                    "alert_id": alert_id,
                    "alert_name": alert.name,
                    "match_info": match_info,
                    "trigger_message": trigger_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "alert_type": condition.alert_type.value if condition else "unknown",
                    "team": condition.team if condition else "",
                    "player_name": condition.player_name if condition else None
                }
                
                await websocket_manager.send_alert_notification(alert.user_id, alert_data)
                logger.info(f"📡 WebSocket notification sent for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
    
    async def record_alert_history(self, alert_id: int, match_info: Dict, trigger_message: str, sms_result: Dict):
        """Record alert trigger in history"""
        try:
            db = next(get_db())
            
            history = AlertHistory(
                alert_id=alert_id,
                match_id=match_info.get("external_id"),
                triggered_at=datetime.utcnow(),
                trigger_message=trigger_message,
                sms_sent=sms_result.get("success", False),
                sms_message_id=sms_result.get("message_sid", ""),
                match_data=str(match_info)
            )
            
            db.add(history)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error recording alert history: {e}")

# Global instance
match_monitor = MatchMonitor() 