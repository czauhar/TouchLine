import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from .metrics_calculator import MatchMetrics

logger = logging.getLogger(__name__)

class ConditionType(Enum):
    """Types of conditions that can be evaluated"""
    GOALS = "goals"
    SCORE_DIFFERENCE = "score_difference"
    POSSESSION = "possession"
    TIME_BASED = "time_based"
    XG = "xg"
    MOMENTUM = "momentum"
    PRESSURE = "pressure"
    WIN_PROBABILITY = "win_probability"
    SEQUENCE = "sequence"
    TIME_WINDOW = "time_window"
    PATTERN = "pattern"

class Operator(Enum):
    """Comparison operators for conditions"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"

class LogicOperator(Enum):
    """Logical operators for combining conditions"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

@dataclass
class Condition:
    """Individual condition definition"""
    condition_type: ConditionType
    team: str
    operator: Operator
    value: Union[float, str, int]
    time_window: Optional[int] = None  # minutes
    description: str = ""

@dataclass
class TimeWindow:
    """Time window for time-based conditions"""
    start_minute: int
    end_minute: int
    description: str = ""

@dataclass
class SequenceCondition:
    """Condition that tracks sequences of events"""
    events: List[Condition]
    time_limit: int  # seconds between events
    description: str = ""

@dataclass
class AdvancedAlertCondition:
    """Advanced alert condition with multi-condition logic"""
    alert_id: int
    name: str
    description: str
    conditions: List[Union[Condition, 'AdvancedAlertCondition']] = field(default_factory=list)
    logic_operator: LogicOperator = LogicOperator.AND
    time_windows: List[TimeWindow] = field(default_factory=list)
    sequences: List[SequenceCondition] = field(default_factory=list)
    is_active: bool = True
    user_phone: str = ""
    
    def add_condition(self, condition: Union[Condition, 'AdvancedAlertCondition']):
        """Add a condition to this alert"""
        self.conditions.append(condition)
    
    def add_time_window(self, time_window: TimeWindow):
        """Add a time window constraint"""
        self.time_windows.append(time_window)
    
    def add_sequence(self, sequence: SequenceCondition):
        """Add a sequence condition"""
        self.sequences.append(sequence)

class AdvancedConditionEvaluator:
    """Evaluates advanced alert conditions with multi-condition logic"""
    
    def __init__(self):
        self.match_history = {}  # fixture_id -> list of match states
        self.sequence_trackers = {}  # alert_id -> sequence tracking data
    
    async def evaluate_advanced_condition(
        self, 
        alert_condition: AdvancedAlertCondition, 
        match_data: Dict, 
        metrics: MatchMetrics
    ) -> tuple[bool, str]:
        """Evaluate an advanced alert condition"""
        try:
            # Check if we're in any required time windows
            if not self._check_time_windows(alert_condition, match_data):
                return False, ""
            
            # Evaluate all conditions
            condition_results = []
            for condition in alert_condition.conditions:
                if isinstance(condition, Condition):
                    result, message = await self._evaluate_single_condition(condition, match_data, metrics)
                    condition_results.append((result, message))
                elif isinstance(condition, AdvancedAlertCondition):
                    result, message = await self.evaluate_advanced_condition(condition, match_data, metrics)
                    condition_results.append((result, message))
            
            # Apply logic operator
            final_result, final_message = self._apply_logic_operator(
                alert_condition.logic_operator, 
                condition_results
            )
            
            # Check sequences
            if final_result and alert_condition.sequences:
                sequence_result = await self._check_sequences(alert_condition, match_data, metrics)
                if not sequence_result:
                    return False, ""
            
            return final_result, final_message
            
        except Exception as e:
            logger.error(f"Error evaluating advanced condition: {e}")
            return False, ""
    
    async def _evaluate_single_condition(
        self, 
        condition: Condition, 
        match_data: Dict, 
        metrics: MatchMetrics
    ) -> tuple[bool, str]:
        """Evaluate a single condition"""
        try:
            match_info = self._format_match_data(match_data)
            
            if condition.condition_type == ConditionType.GOALS:
                return self._evaluate_goals_condition(condition, match_info)
            elif condition.condition_type == ConditionType.SCORE_DIFFERENCE:
                return self._evaluate_score_difference_condition(condition, match_info)
            elif condition.condition_type == ConditionType.TIME_BASED:
                return self._evaluate_time_based_condition(condition, match_info)
            elif condition.condition_type == ConditionType.XG:
                return self._evaluate_xg_condition(condition, metrics)
            elif condition.condition_type == ConditionType.MOMENTUM:
                return self._evaluate_momentum_condition(condition, metrics)
            elif condition.condition_type == ConditionType.PRESSURE:
                return self._evaluate_pressure_condition(condition, metrics)
            elif condition.condition_type == ConditionType.WIN_PROBABILITY:
                return self._evaluate_win_probability_condition(condition, metrics)
            else:
                return False, f"Unknown condition type: {condition.condition_type}"
                
        except Exception as e:
            logger.error(f"Error evaluating single condition: {e}")
            return False, ""
    
    def _evaluate_goals_condition(self, condition: Condition, match_info: Dict) -> tuple[bool, str]:
        """Evaluate goals-based condition"""
        home_team = match_info.get("home_team", "")
        away_team = match_info.get("away_team", "")
        home_score = match_info.get("home_score", 0)
        away_score = match_info.get("away_score", 0)
        
        target_team = condition.team
        team_score = home_score if target_team.lower() in home_team.lower() else away_score
        
        result = self._compare_values(team_score, condition.operator, condition.value)
        message = f"{target_team} goals: {team_score} {condition.operator.value} {condition.value}" if result else ""
        
        return result, message
    
    def _evaluate_score_difference_condition(self, condition: Condition, match_info: Dict) -> tuple[bool, str]:
        """Evaluate score difference condition"""
        home_team = match_info.get("home_team", "")
        away_team = match_info.get("away_team", "")
        home_score = match_info.get("home_score", 0)
        away_score = match_info.get("away_score", 0)
        
        target_team = condition.team
        if target_team.lower() in home_team.lower():
            difference = home_score - away_score
        else:
            difference = away_score - home_score
        
        result = self._compare_values(difference, condition.operator, condition.value)
        message = f"{target_team} lead: {difference} {condition.operator.value} {condition.value}" if result else ""
        
        return result, message
    
    def _evaluate_time_based_condition(self, condition: Condition, match_info: Dict) -> tuple[bool, str]:
        """Evaluate time-based condition"""
        elapsed = match_info.get("elapsed", 0)
        
        if condition.time_window and elapsed >= condition.time_window:
            return True, f"Match time: {elapsed} >= {condition.time_window} minutes"
        
        return False, ""
    
    def _evaluate_xg_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate xG-based condition"""
        target_team = condition.team
        team_xg = metrics.home_xg if target_team.lower() in metrics.home_team.lower() else metrics.away_xg
        
        result = self._compare_values(team_xg, condition.operator, condition.value)
        message = f"{target_team} xG: {team_xg:.2f} {condition.operator.value} {condition.value}" if result else ""
        
        return result, message
    
    def _evaluate_momentum_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate momentum-based condition"""
        target_team = condition.team
        team_momentum = metrics.home_momentum if target_team.lower() in metrics.home_team.lower() else metrics.away_momentum
        
        result = self._compare_values(team_momentum, condition.operator, condition.value)
        message = f"{target_team} momentum: {team_momentum:.1f} {condition.operator.value} {condition.value}" if result else ""
        
        return result, message
    
    def _evaluate_pressure_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate pressure-based condition"""
        target_team = condition.team
        team_pressure = metrics.home_pressure_index if target_team.lower() in metrics.home_team.lower() else metrics.away_pressure_index
        
        result = self._compare_values(team_pressure, condition.operator, condition.value)
        message = f"{target_team} pressure: {team_pressure:.2f} {condition.operator.value} {condition.value}" if result else ""
        
        return result, message
    
    def _evaluate_win_probability_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate win probability condition"""
        target_team = condition.team
        team_win_prob = metrics.home_win_probability if target_team.lower() in metrics.home_team.lower() else metrics.away_win_probability
        
        result = self._compare_values(team_win_prob, condition.operator, condition.value)
        message = f"{target_team} win probability: {team_win_prob:.1%} {condition.operator.value} {condition.value:.1%}" if result else ""
        
        return result, message
    
    def _compare_values(self, actual: Union[float, int, str], operator: Operator, expected: Union[float, int, str]) -> bool:
        """Compare values using the specified operator"""
        try:
            if operator == Operator.EQUALS:
                return actual == expected
            elif operator == Operator.NOT_EQUALS:
                return actual != expected
            elif operator == Operator.GREATER_THAN:
                return actual > expected
            elif operator == Operator.GREATER_EQUAL:
                return actual >= expected
            elif operator == Operator.LESS_THAN:
                return actual < expected
            elif operator == Operator.LESS_EQUAL:
                return actual <= expected
            elif operator == Operator.CONTAINS:
                return str(expected).lower() in str(actual).lower()
            elif operator == Operator.NOT_CONTAINS:
                return str(expected).lower() not in str(actual).lower()
            else:
                return False
        except Exception as e:
            logger.error(f"Error comparing values: {e}")
            return False
    
    def _check_time_windows(self, alert_condition: AdvancedAlertCondition, match_data: Dict) -> bool:
        """Check if current match time is within any required time windows"""
        if not alert_condition.time_windows:
            return True  # No time window constraints
        
        elapsed = match_data.get("fixture", {}).get("status", {}).get("elapsed", 0)
        
        for time_window in alert_condition.time_windows:
            if time_window.start_minute <= elapsed <= time_window.end_minute:
                return True
        
        return False
    
    async def _check_sequences(self, alert_condition: AdvancedAlertCondition, match_data: Dict, metrics: MatchMetrics) -> bool:
        """Check sequence conditions"""
        fixture_id = match_data.get("fixture", {}).get("id")
        if not fixture_id:
            return False
        
        # Initialize sequence tracker if needed
        if fixture_id not in self.sequence_trackers:
            self.sequence_trackers[fixture_id] = {}
        
        if alert_condition.alert_id not in self.sequence_trackers[fixture_id]:
            self.sequence_trackers[fixture_id][alert_condition.alert_id] = {
                "sequences": {},
                "last_update": datetime.now()
            }
        
        tracker = self.sequence_trackers[fixture_id][alert_condition.alert_id]
        
        for sequence in alert_condition.sequences:
            sequence_id = id(sequence)
            if sequence_id not in tracker["sequences"]:
                tracker["sequences"][sequence_id] = {
                    "events": [],
                    "start_time": datetime.now()
                }
            
            # Check if sequence is still valid (within time limit)
            sequence_data = tracker["sequences"][sequence_id]
            time_elapsed = (datetime.now() - sequence_data["start_time"]).total_seconds()
            
            if time_elapsed > sequence.time_limit:
                # Reset sequence if time limit exceeded
                sequence_data["events"] = []
                sequence_data["start_time"] = datetime.now()
            
            # Check current match state against sequence events
            for event in sequence.events:
                result, _ = await self._evaluate_single_condition(event, match_data, metrics)
                if result:
                    # Add event to sequence if not already present
                    event_key = f"{event.condition_type}_{event.team}_{event.value}"
                    if event_key not in [e.get("key") for e in sequence_data["events"]]:
                        sequence_data["events"].append({
                            "key": event_key,
                            "condition": event,
                            "timestamp": datetime.now()
                        })
            
            # Check if sequence is complete
            if len(sequence_data["events"]) >= len(sequence.events):
                return True
        
        return False
    
    def _apply_logic_operator(self, logic_operator: LogicOperator, condition_results: List[tuple[bool, str]]) -> tuple[bool, str]:
        """Apply logical operator to condition results"""
        if not condition_results:
            return False, ""
        
        if logic_operator == LogicOperator.AND:
            all_true = all(result for result, _ in condition_results)
            messages = [msg for _, msg in condition_results if msg]
            return all_true, " AND ".join(messages) if all_true else ""
        
        elif logic_operator == LogicOperator.OR:
            any_true = any(result for result, _ in condition_results)
            messages = [msg for result, msg in condition_results if result and msg]
            return any_true, " OR ".join(messages) if any_true else ""
        
        elif logic_operator == LogicOperator.NOT:
            # NOT operator applies to the first condition only
            if condition_results:
                result, message = condition_results[0]
                return not result, f"NOT {message}" if not result else ""
        
        return False, ""
    
    def _format_match_data(self, match_data: Dict) -> Dict:
        """Format match data for condition evaluation"""
        fixture = match_data.get("fixture", {})
        teams = match_data.get("teams", {})
        goals = match_data.get("goals", {})
        
        return {
            "home_team": teams.get("home", {}).get("name", ""),
            "away_team": teams.get("away", {}).get("name", ""),
            "home_score": goals.get("home") or 0,
            "away_score": goals.get("away") or 0,
            "elapsed": fixture.get("status", {}).get("elapsed", 0),
            "status": fixture.get("status", {}).get("short", "")
        }

# Global instance
advanced_evaluator = AdvancedConditionEvaluator() 