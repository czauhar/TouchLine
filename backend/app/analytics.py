import math
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class MatchMetrics:
    """Comprehensive match metrics for analysis"""
    fixture_id: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    elapsed: int
    league: str
    
    # Basic stats
    home_shots: int = 0
    away_shots: int = 0
    home_shots_on_target: int = 0
    away_shots_on_target: int = 0
    home_possession: float = 50.0
    away_possession: float = 50.0
    home_corners: int = 0
    away_corners: int = 0
    home_yellow_cards: int = 0
    away_yellow_cards: int = 0
    home_red_cards: int = 0
    away_red_cards: int = 0
    
    # Calculated metrics
    home_xg: float = 0.0
    away_xg: float = 0.0
    home_momentum: float = 0.0
    away_momentum: float = 0.0
    home_pressure_index: float = 0.0
    away_pressure_index: float = 0.0
    home_win_probability: float = 0.33
    away_win_probability: float = 0.33
    draw_probability: float = 0.34

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

# =============================================================================
# Analytics Engine
# =============================================================================

class AnalyticsEngine:
    """Combined analytics engine for metrics calculation and condition evaluation"""
    
    def __init__(self):
        # Historical performance weights
        self.league_weights = {
            "Premier League": 1.0,
            "La Liga": 0.95,
            "Bundesliga": 0.92,
            "Serie A": 0.90,
            "Ligue 1": 0.88,
            "Champions League": 1.1,
            "Europa League": 1.05
        }
        
        # xG conversion rates
        self.xg_conversion_rates = {
            "shot_on_target": 0.25,
            "shot_off_target": 0.05,
            "corner": 0.08,
            "possession_advantage": 0.02
        }
        
        # Condition evaluation state
        self.match_history = {}  # fixture_id -> list of match states
        self.sequence_trackers = {}  # alert_id -> sequence tracking data
    
    def calculate_all_metrics(self, match_data: Dict) -> MatchMetrics:
        """Calculate all advanced metrics for a match"""
        metrics = MatchMetrics(
            fixture_id=match_data.get("fixture", {}).get("id", 0),
            home_team=match_data.get("teams", {}).get("home", {}).get("name", ""),
            away_team=match_data.get("teams", {}).get("away", {}).get("name", ""),
            home_score=match_data.get("goals", {}).get("home", 0),
            away_score=match_data.get("goals", {}).get("away", 0),
            elapsed=match_data.get("fixture", {}).get("status", {}).get("elapsed", 0),
            league=match_data.get("league", {}).get("name", "")
        )
        
        # Extract basic stats from match data
        self._extract_basic_stats(metrics, match_data)
        
        # Calculate advanced metrics
        self._calculate_xg(metrics)
        self._calculate_momentum(metrics)
        self._calculate_pressure_index(metrics)
        self._calculate_win_probabilities(metrics)
        
        return metrics
    
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
    
    def get_team_metrics(self, metrics: MatchMetrics, team_name: str) -> Dict:
        """Get metrics for a specific team"""
        if team_name.lower() in metrics.home_team.lower():
            return {
                "score": metrics.home_score,
                "shots": metrics.home_shots,
                "shots_on_target": metrics.home_shots_on_target,
                "possession": metrics.home_possession,
                "xg": metrics.home_xg,
                "momentum": metrics.home_momentum,
                "pressure_index": metrics.home_pressure_index,
                "win_probability": metrics.home_win_probability
            }
        elif team_name.lower() in metrics.away_team.lower():
            return {
                "score": metrics.away_score,
                "shots": metrics.away_shots,
                "shots_on_target": metrics.away_shots_on_target,
                "possession": metrics.away_possession,
                "xg": metrics.away_xg,
                "momentum": metrics.away_momentum,
                "pressure_index": metrics.away_pressure_index,
                "win_probability": metrics.away_win_probability
            }
        else:
            return {}
    
    # =============================================================================
    # Private Methods - Metrics Calculation
    # =============================================================================
    
    def _extract_basic_stats(self, metrics: MatchMetrics, match_data: Dict):
        """Extract basic statistics from match data"""
        total_elapsed = metrics.elapsed
        score_diff = abs(metrics.home_score - metrics.away_score)
        
        # Estimate shots based on goals and time
        total_goals = metrics.home_score + metrics.away_score
        estimated_total_shots = max(8, total_goals * 4 + total_elapsed // 10)
        
        # Distribute shots based on possession (simplified)
        home_shot_ratio = 0.5 + (metrics.home_score - metrics.away_score) * 0.1
        metrics.home_shots = int(estimated_total_shots * home_shot_ratio)
        metrics.away_shots = estimated_total_shots - metrics.home_shots
        
        # Shots on target (roughly 1/3 of total shots)
        metrics.home_shots_on_target = max(metrics.home_score, metrics.home_shots // 3)
        metrics.away_shots_on_target = max(metrics.away_score, metrics.away_shots // 3)
        
        # Possession (based on score and time)
        if total_elapsed > 0:
            possession_advantage = (metrics.home_score - metrics.away_score) * 5
            metrics.home_possession = 50 + possession_advantage
            metrics.away_possession = 100 - metrics.home_possession
        else:
            metrics.home_possession = 50
            metrics.away_possession = 50
    
    def _calculate_xg(self, metrics: MatchMetrics):
        """Calculate Expected Goals (xG) for both teams"""
        # Base xG from shots on target
        metrics.home_xg = metrics.home_shots_on_target * self.xg_conversion_rates["shot_on_target"]
        metrics.away_xg = metrics.away_shots_on_target * self.xg_conversion_rates["shot_on_target"]
        
        # Add xG from possession advantage
        possession_bonus = (metrics.home_possession - 50) * self.xg_conversion_rates["possession_advantage"]
        metrics.home_xg += possession_bonus
        metrics.away_xg -= possession_bonus
        
        # Ensure xG is non-negative
        metrics.home_xg = max(0, metrics.home_xg)
        metrics.away_xg = max(0, metrics.away_xg)
    
    def _calculate_momentum(self, metrics: MatchMetrics):
        """Calculate momentum score for both teams"""
        # Base momentum from current score
        home_momentum = metrics.home_score * 10
        away_momentum = metrics.away_score * 10
        
        # Add possession momentum
        home_momentum += (metrics.home_possession - 50) * 0.5
        away_momentum += (metrics.away_possession - 50) * 0.5
        
        # Time-based momentum (later in game = higher stakes)
        time_multiplier = min(2.0, metrics.elapsed / 45.0)
        home_momentum *= time_multiplier
        away_momentum *= time_multiplier
        
        # Score difference momentum
        score_diff = metrics.home_score - metrics.away_score
        if score_diff > 0:
            home_momentum += score_diff * 5
        else:
            away_momentum += abs(score_diff) * 5
        
        metrics.home_momentum = home_momentum
        metrics.away_momentum = away_momentum
    
    def _calculate_pressure_index(self, metrics: MatchMetrics):
        """Calculate pressure index for both teams"""
        # Time pressure (more pressure in final minutes)
        time_pressure = min(1.0, metrics.elapsed / 90.0)
        
        # Score pressure
        score_diff = metrics.home_score - metrics.away_score
        if score_diff == 0:
            # Tied game = high pressure for both
            home_pressure = 0.8
            away_pressure = 0.8
        elif score_diff > 0:
            # Home team leading
            home_pressure = 0.3 + (time_pressure * 0.4)  # Defending lead
            away_pressure = 0.9 + (time_pressure * 0.1)  # Chasing game
        else:
            # Away team leading
            home_pressure = 0.9 + (time_pressure * 0.1)  # Chasing game
            away_pressure = 0.3 + (time_pressure * 0.4)  # Defending lead
        
        # League importance multiplier
        league_weight = self.league_weights.get(metrics.league, 1.0)
        home_pressure *= league_weight
        away_pressure *= league_weight
        
        metrics.home_pressure_index = min(1.0, home_pressure)
        metrics.away_pressure_index = min(1.0, away_pressure)
    
    def _calculate_win_probabilities(self, metrics: MatchMetrics):
        """Calculate win/draw probabilities for both teams"""
        total_goals = metrics.home_score + metrics.away_score
        time_remaining = max(0, 90 - metrics.elapsed)
        
        # Base probabilities from current score
        if metrics.home_score > metrics.away_score:
            metrics.home_win_probability = 0.7
            metrics.away_win_probability = 0.1
            metrics.draw_probability = 0.2
        elif metrics.away_score > metrics.home_score:
            metrics.home_win_probability = 0.1
            metrics.away_win_probability = 0.7
            metrics.draw_probability = 0.2
        else:
            metrics.home_win_probability = 0.35
            metrics.away_win_probability = 0.35
            metrics.draw_probability = 0.3
        
        # Adjust based on time remaining and xG
        if time_remaining > 0:
            xg_adjustment = (metrics.home_xg - metrics.away_xg) * 0.1
            metrics.home_win_probability += xg_adjustment
            metrics.away_win_probability -= xg_adjustment
            
            # Normalize probabilities
            total = metrics.home_win_probability + metrics.away_win_probability + metrics.draw_probability
            metrics.home_win_probability /= total
            metrics.away_win_probability /= total
            metrics.draw_probability /= total
    
    # =============================================================================
    # Private Methods - Condition Evaluation
    # =============================================================================
    
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
        result = self._compare_values(elapsed, condition.operator, condition.value)
        message = f"Time elapsed: {elapsed} {condition.operator.value} {condition.value}" if result else ""
        return result, message
    
    def _evaluate_xg_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate xG condition"""
        team_metrics = self.get_team_metrics(metrics, condition.team)
        xg = team_metrics.get("xg", 0)
        result = self._compare_values(xg, condition.operator, condition.value)
        message = f"{condition.team} xG: {xg:.2f} {condition.operator.value} {condition.value}" if result else ""
        return result, message
    
    def _evaluate_momentum_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate momentum condition"""
        team_metrics = self.get_team_metrics(metrics, condition.team)
        momentum = team_metrics.get("momentum", 0)
        result = self._compare_values(momentum, condition.operator, condition.value)
        message = f"{condition.team} momentum: {momentum:.2f} {condition.operator.value} {condition.value}" if result else ""
        return result, message
    
    def _evaluate_pressure_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate pressure condition"""
        team_metrics = self.get_team_metrics(metrics, condition.team)
        pressure = team_metrics.get("pressure_index", 0)
        result = self._compare_values(pressure, condition.operator, condition.value)
        message = f"{condition.team} pressure: {pressure:.2f} {condition.operator.value} {condition.value}" if result else ""
        return result, message
    
    def _evaluate_win_probability_condition(self, condition: Condition, metrics: MatchMetrics) -> tuple[bool, str]:
        """Evaluate win probability condition"""
        team_metrics = self.get_team_metrics(metrics, condition.team)
        win_prob = team_metrics.get("win_probability", 0)
        result = self._compare_values(win_prob, condition.operator, condition.value)
        message = f"{condition.team} win probability: {win_prob:.2f} {condition.operator.value} {condition.value}" if result else ""
        return result, message
    
    def _compare_values(self, actual: Union[float, int, str], operator: Operator, expected: Union[float, int, str]) -> bool:
        """Compare actual value with expected value using operator"""
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
                return str(expected) in str(actual)
            elif operator == Operator.NOT_CONTAINS:
                return str(expected) not in str(actual)
            else:
                return False
        except Exception:
            return False
    
    def _check_time_windows(self, alert_condition: AdvancedAlertCondition, match_data: Dict) -> bool:
        """Check if current time is within any required time windows"""
        if not alert_condition.time_windows:
            return True
        
        elapsed = match_data.get("fixture", {}).get("status", {}).get("elapsed", 0)
        
        for time_window in alert_condition.time_windows:
            if time_window.start_minute <= elapsed <= time_window.end_minute:
                return True
        
        return False
    
    async def _check_sequences(self, alert_condition: AdvancedAlertCondition, match_data: Dict, metrics: MatchMetrics) -> bool:
        """Check if sequence conditions are met"""
        if not alert_condition.sequences:
            return True
        
        fixture_id = match_data.get("fixture", {}).get("id", 0)
        current_time = datetime.utcnow()
        
        for sequence in alert_condition.sequences:
            sequence_key = f"{alert_condition.alert_id}_{fixture_id}"
            
            if sequence_key not in self.sequence_trackers:
                self.sequence_trackers[sequence_key] = {
                    "events": [],
                    "start_time": current_time
                }
            
            tracker = self.sequence_trackers[sequence_key]
            
            # Check if sequence is still valid (within time limit)
            time_diff = (current_time - tracker["start_time"]).total_seconds()
            if time_diff > sequence.time_limit:
                # Reset sequence if time limit exceeded
                tracker["events"] = []
                tracker["start_time"] = current_time
            
            # Evaluate current event
            for event in sequence.events:
                result, _ = await self._evaluate_single_condition(event, match_data, metrics)
                if result:
                    # Add event to sequence
                    tracker["events"].append({
                        "event": event,
                        "time": current_time
                    })
                    
                    # Check if all events in sequence are complete
                    if len(tracker["events"]) >= len(sequence.events):
                        return True
        
        return False
    
    def _apply_logic_operator(self, logic_operator: LogicOperator, condition_results: List[tuple[bool, str]]) -> tuple[bool, str]:
        """Apply logic operator to condition results"""
        if not condition_results:
            return False, ""
        
        results = [result[0] for result in condition_results]
        messages = [result[1] for result in condition_results if result[1]]
        
        if logic_operator == LogicOperator.AND:
            final_result = all(results)
        elif logic_operator == LogicOperator.OR:
            final_result = any(results)
        elif logic_operator == LogicOperator.NOT:
            final_result = not any(results)
        else:
            final_result = False
        
        final_message = " AND ".join(messages) if messages else ""
        return final_result, final_message
    
    def _format_match_data(self, match_data: Dict) -> Dict:
        """Format match data for condition evaluation"""
        return {
            "home_team": match_data.get("teams", {}).get("home", {}).get("name", ""),
            "away_team": match_data.get("teams", {}).get("away", {}).get("name", ""),
            "home_score": match_data.get("goals", {}).get("home", 0),
            "away_score": match_data.get("goals", {}).get("away", 0),
            "elapsed": match_data.get("fixture", {}).get("status", {}).get("elapsed", 0)
        }

# Global instance
analytics_engine = AnalyticsEngine() 