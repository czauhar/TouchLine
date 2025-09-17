"""
TouchLine Custom Metrics Service
Allows users to create and evaluate custom derived metrics
"""

import re
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of custom metrics"""
    TEAM_BASED = "team_based"
    PLAYER_BASED = "player_based"
    MATCH_BASED = "match_based"
    SEQUENCE_BASED = "sequence_based"
    TIME_BASED = "time_based"

class FormulaOperator(Enum):
    """Mathematical operators for formulas"""
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    POWER = "**"
    MIN = "min"
    MAX = "max"
    AVERAGE = "avg"
    COUNT = "count"
    SUM = "sum"

@dataclass
class CustomMetric:
    """Custom metric definition"""
    id: Optional[int] = None
    user_id: int = 0
    name: str = ""
    description: str = ""
    formula: str = ""
    metric_type: MetricType = MetricType.TEAM_BASED
    variables: Dict[str, str] = field(default_factory=dict)  # variable_name -> description
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def validate_formula(self) -> tuple[bool, str]:
        """Validate the formula syntax and variables"""
        try:
            # Check for basic syntax
            if not self.formula.strip():
                return False, "Formula cannot be empty"
            
            # Check for dangerous operations
            dangerous_patterns = [
                r'import\s+',
                r'exec\s*\(',
                r'eval\s*\(',
                r'__\w+__',
                r'open\s*\(',
                r'file\s*\(',
                r'os\.',
                r'sys\.',
                r'subprocess\.'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, self.formula, re.IGNORECASE):
                    return False, f"Dangerous operation detected: {pattern}"
            
            # Check for balanced parentheses
            if self.formula.count('(') != self.formula.count(')'):
                return False, "Unbalanced parentheses"
            
            # Check for valid operators
            valid_operators = ['+', '-', '*', '/', '%', '**', '(', ')', ' ']
            valid_functions = ['min', 'max', 'avg', 'count', 'sum', 'abs', 'round']
            
            # Extract variables (words that are not operators or functions)
            words = re.findall(r'\b\w+\b', self.formula)
            for word in words:
                if (word not in valid_functions and 
                    word not in self.variables and 
                    not word.isdigit()):
                    return False, f"Unknown variable or function: {word}"
            
            return True, "Formula is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

class CustomMetricEngine:
    """Engine for evaluating custom metrics"""
    
    def __init__(self):
        self.metric_cache = {}  # metric_id -> compiled_formula
        self.variable_extractors = {
            # Team-based variables
            "team_goals": self._extract_team_goals,
            "team_shots": self._extract_team_shots,
            "team_shots_on_target": self._extract_team_shots_on_target,
            "team_possession": self._extract_team_possession,
            "team_corners": self._extract_team_corners,
            "team_fouls": self._extract_team_fouls,
            "team_yellow_cards": self._extract_team_yellow_cards,
            "team_red_cards": self._extract_team_red_cards,
            "team_xg": self._extract_team_xg,
            "team_momentum": self._extract_team_momentum,
            "team_pressure": self._extract_team_pressure,
            
            # Player-based variables
            "player_goals": self._extract_player_goals,
            "player_assists": self._extract_player_assists,
            "player_shots": self._extract_player_shots,
            "player_passes": self._extract_player_passes,
            "player_tackles": self._extract_player_tackles,
            "player_rating": self._extract_player_rating,
            "player_minutes": self._extract_player_minutes,
            
            # Match-based variables
            "total_goals": self._extract_total_goals,
            "total_shots": self._extract_total_shots,
            "match_elapsed": self._extract_match_elapsed,
            "score_difference": self._extract_score_difference,
            "match_intensity": self._extract_match_intensity,
            
            # Time-based variables
            "first_half_goals": self._extract_first_half_goals,
            "second_half_goals": self._extract_second_half_goals,
            "last_10_minutes_goals": self._extract_last_10_minutes_goals,
        }
    
    def evaluate_metric(self, metric: CustomMetric, match_data, team_name: str = "", player_name: str = "") -> float:
        """Evaluate a custom metric for given match data"""
        try:
            # Extract variables
            variables = {}
            for var_name in metric.variables:
                if var_name in self.variable_extractors:
                    variables[var_name] = self.variable_extractors[var_name](match_data, team_name, player_name)
                else:
                    variables[var_name] = 0.0  # Default value
            
            # Create safe evaluation environment
            safe_dict = {
                **variables,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sum': sum,
                'len': len
            }
            
            # Evaluate formula
            result = eval(metric.formula, {"__builtins__": {}}, safe_dict)
            
            # Ensure result is numeric
            if isinstance(result, (int, float)):
                return float(result)
            else:
                logger.warning(f"Metric {metric.name} returned non-numeric result: {result}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error evaluating metric {metric.name}: {e}")
            return 0.0
    
    def _extract_team_goals(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team goals"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_score)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_score)
        else:  # Dict object
            home_team = match_data.get("teams", {}).get("home", {}).get("name", "")
            away_team = match_data.get("teams", {}).get("away", {}).get("name", "")
            home_score = match_data.get("goals", {}).get("home", 0)
            away_score = match_data.get("goals", {}).get("away", 0)
            
            if team_name.lower() in home_team.lower():
                return float(home_score)
            elif team_name.lower() in away_team.lower():
                return float(away_score)
        
        return 0.0
    
    def _extract_team_shots(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team shots"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_shots)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_shots)
        else:  # Dict object
            # Extract from stats if available
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    return float(stat.get("statistics", {}).get("Total Shots", 0))
        
        return 0.0
    
    def _extract_team_shots_on_target(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team shots on target"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_shots_on_target)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_shots_on_target)
        else:  # Dict object
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    return float(stat.get("statistics", {}).get("Shots on Goal", 0))
        
        return 0.0
    
    def _extract_team_possession(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team possession"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_possession)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_possession)
        else:  # Dict object
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    possession_str = stat.get("statistics", {}).get("Ball Possession", "0%")
                    return float(possession_str.replace("%", ""))
        
        return 50.0  # Default 50-50 split
    
    def _extract_team_corners(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team corners"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_corners)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_corners)
        else:  # Dict object
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    return float(stat.get("statistics", {}).get("Corner Kicks", 0))
        
        return 0.0
    
    def _extract_team_fouls(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team fouls"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_fouls)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_fouls)
        else:  # Dict object
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    return float(stat.get("statistics", {}).get("Fouls", 0))
        
        return 0.0
    
    def _extract_team_yellow_cards(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team yellow cards"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_yellow_cards)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_yellow_cards)
        else:  # Dict object
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    return float(stat.get("statistics", {}).get("Yellow Cards", 0))
        
        return 0.0
    
    def _extract_team_red_cards(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team red cards"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_red_cards)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_red_cards)
        else:  # Dict object
            stats = match_data.get("statistics", [])
            for stat in stats:
                if stat.get("team", {}).get("name", "").lower() == team_name.lower():
                    return float(stat.get("statistics", {}).get("Red Cards", 0))
        
        return 0.0
    
    def _extract_team_xg(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team expected goals"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_xg)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_xg)
        else:  # Dict object
            # xG might not be available in basic match data
            return 0.0
        
        return 0.0
    
    def _extract_team_momentum(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team momentum"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_momentum)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_momentum)
        else:  # Dict object
            # Momentum might not be available in basic match data
            return 50.0
        
        return 50.0
    
    def _extract_team_pressure(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract team pressure index"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            if team_name.lower() in match_data.home_team.lower():
                return float(match_data.home_pressure)
            elif team_name.lower() in match_data.away_team.lower():
                return float(match_data.away_pressure)
        else:  # Dict object
            # Pressure might not be available in basic match data
            return 50.0
        
        return 50.0
    
    # Player-based extractors
    def _extract_player_goals(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player goals"""
        if not player_name:
            return 0.0
        
        # This would need to be implemented based on player statistics
        # For now, return 0 as player stats might not be available
        return 0.0
    
    def _extract_player_assists(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player assists"""
        if not player_name:
            return 0.0
        return 0.0
    
    def _extract_player_shots(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player shots"""
        if not player_name:
            return 0.0
        return 0.0
    
    def _extract_player_passes(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player passes"""
        if not player_name:
            return 0.0
        return 0.0
    
    def _extract_player_tackles(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player tackles"""
        if not player_name:
            return 0.0
        return 0.0
    
    def _extract_player_rating(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player rating"""
        if not player_name:
            return 0.0
        return 0.0
    
    def _extract_player_minutes(self, match_data, team_name: str, player_name: str) -> float:
        """Extract player minutes played"""
        if not player_name:
            return 0.0
        return 0.0
    
    # Match-based extractors
    def _extract_total_goals(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract total goals in match"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            return float(match_data.home_score + match_data.away_score)
        else:  # Dict object
            home_score = match_data.get("goals", {}).get("home", 0)
            away_score = match_data.get("goals", {}).get("away", 0)
            return float(home_score + away_score)
    
    def _extract_total_shots(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract total shots in match"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            return float(match_data.home_shots + match_data.away_shots)
        else:  # Dict object
            # Would need to extract from statistics
            return 0.0
    
    def _extract_match_elapsed(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract match elapsed time"""
        if hasattr(match_data, 'elapsed_time'):  # MatchData object
            return float(match_data.elapsed_time or 0)
        else:  # Dict object
            return float(match_data.get("fixture", {}).get("status", {}).get("elapsed", 0))
    
    def _extract_score_difference(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract score difference"""
        if hasattr(match_data, 'home_team'):  # MatchData object
            return float(abs(match_data.home_score - match_data.away_score))
        else:  # Dict object
            home_score = match_data.get("goals", {}).get("home", 0)
            away_score = match_data.get("goals", {}).get("away", 0)
            return float(abs(home_score - away_score))
    
    def _extract_match_intensity(self, match_data, team_name: str, player_name: str = "") -> float:
        """Calculate match intensity based on various factors"""
        total_goals = self._extract_total_goals(match_data, team_name, player_name)
        total_shots = self._extract_total_shots(match_data, team_name, player_name)
        elapsed = self._extract_match_elapsed(match_data, team_name, player_name)
        
        if elapsed == 0:
            return 0.0
        
        # Simple intensity formula: (goals + shots/10) / (elapsed/90)
        intensity = (total_goals + total_shots / 10) / (elapsed / 90)
        return min(intensity, 100.0)  # Cap at 100
    
    # Time-based extractors
    def _extract_first_half_goals(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract goals in first half (0-45 minutes)"""
        elapsed = self._extract_match_elapsed(match_data, team_name, player_name)
        if elapsed <= 45:
            return self._extract_team_goals(match_data, team_name, player_name)
        return 0.0
    
    def _extract_second_half_goals(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract goals in second half (46-90 minutes)"""
        elapsed = self._extract_match_elapsed(match_data, team_name, player_name)
        if 46 <= elapsed <= 90:
            return self._extract_team_goals(match_data, team_name, player_name)
        return 0.0
    
    def _extract_last_10_minutes_goals(self, match_data, team_name: str, player_name: str = "") -> float:
        """Extract goals in last 10 minutes"""
        elapsed = self._extract_match_elapsed(match_data, team_name, player_name)
        if elapsed >= 80:
            return self._extract_team_goals(match_data, team_name, player_name)
        return 0.0

class CustomMetricService:
    """Service for managing custom metrics"""
    
    def __init__(self):
        self.engine = CustomMetricEngine()
    
    def create_metric(self, user_id: int, name: str, description: str, formula: str, 
                     metric_type: MetricType, variables: Dict[str, str]) -> CustomMetric:
        """Create a new custom metric"""
        metric = CustomMetric(
            user_id=user_id,
            name=name,
            description=description,
            formula=formula,
            metric_type=metric_type,
            variables=variables
        )
        
        # Validate the metric
        is_valid, error_message = metric.validate_formula()
        if not is_valid:
            raise ValueError(f"Invalid metric: {error_message}")
        
        return metric
    
    def get_user_metrics(self, user_id: int) -> List[CustomMetric]:
        """Get all custom metrics for a user"""
        # This would typically query the database
        # For now, return empty list
        return []
    
    def evaluate_user_metrics(self, user_id: int, match_data, team_name: str = "", player_name: str = "") -> Dict[str, float]:
        """Evaluate all custom metrics for a user"""
        metrics = self.get_user_metrics(user_id)
        results = {}
        
        for metric in metrics:
            if metric.is_active:
                try:
                    value = self.engine.evaluate_metric(metric, match_data, team_name, player_name)
                    results[metric.name] = value
                except Exception as e:
                    logger.error(f"Error evaluating metric {metric.name}: {e}")
                    results[metric.name] = 0.0
        
        return results

# Global instances
custom_metric_engine = CustomMetricEngine()
custom_metric_service = CustomMetricService() 