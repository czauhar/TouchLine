import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

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

class MetricsCalculator:
    """Advanced soccer metrics calculator"""
    
    def __init__(self):
        # Historical performance weights (can be updated with real data)
        self.league_weights = {
            "Premier League": 1.0,
            "La Liga": 0.95,
            "Bundesliga": 0.92,
            "Serie A": 0.90,
            "Ligue 1": 0.88,
            "Champions League": 1.1,
            "Europa League": 1.05
        }
        
        # xG conversion rates (simplified model)
        self.xg_conversion_rates = {
            "shot_on_target": 0.25,
            "shot_off_target": 0.05,
            "corner": 0.08,
            "possession_advantage": 0.02
        }
    
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
    
    def _extract_basic_stats(self, metrics: MatchMetrics, match_data: Dict):
        """Extract basic statistics from match data"""
        # This would normally come from detailed match statistics API
        # For now, we'll use simplified estimates based on score and time
        
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
        # Simplified xG model based on shots and possession
        
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
        # Momentum based on recent scoring and possession
        
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
        # Pressure based on time, score, and situation
        
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
        # Based on current score, xG, and time remaining
        
        total_goals = metrics.home_score + metrics.away_score
        time_remaining = max(0, 90 - metrics.elapsed)
        
        # Base probabilities from current score
        if metrics.home_score > metrics.away_score:
            home_win_base = 0.7
            away_win_base = 0.1
            draw_base = 0.2
        elif metrics.away_score > metrics.home_score:
            home_win_base = 0.1
            away_win_base = 0.7
            draw_base = 0.2
        else:
            home_win_base = 0.3
            away_win_base = 0.3
            draw_base = 0.4
        
        # Adjust based on xG
        xg_diff = metrics.home_xg - metrics.away_xg
        xg_adjustment = xg_diff * 0.1
        
        home_win_base += xg_adjustment
        away_win_base -= xg_adjustment
        
        # Adjust based on time remaining
        if time_remaining < 10:
            # Late game - current score more important
            time_factor = 0.8
        else:
            # Early game - xG more important
            time_factor = 0.3
        
        # Final probabilities
        metrics.home_win_probability = max(0.01, min(0.95, home_win_base * (1 - time_factor) + (metrics.home_score > metrics.away_score) * time_factor))
        metrics.away_win_probability = max(0.01, min(0.95, away_win_base * (1 - time_factor) + (metrics.away_score > metrics.home_score) * time_factor))
        metrics.draw_probability = 1 - metrics.home_win_probability - metrics.away_win_probability
        
        # Normalize to ensure probabilities sum to 1
        total = metrics.home_win_probability + metrics.away_win_probability + metrics.draw_probability
        metrics.home_win_probability /= total
        metrics.away_win_probability /= total
        metrics.draw_probability /= total
    
    def get_team_metrics(self, metrics: MatchMetrics, team_name: str) -> Dict:
        """Get metrics for a specific team"""
        is_home = team_name.lower() in metrics.home_team.lower()
        
        return {
            "team": team_name,
            "score": metrics.home_score if is_home else metrics.away_score,
            "opponent_score": metrics.away_score if is_home else metrics.home_score,
            "xg": metrics.home_xg if is_home else metrics.away_xg,
            "momentum": metrics.home_momentum if is_home else metrics.away_momentum,
            "pressure_index": metrics.home_pressure_index if is_home else metrics.away_pressure_index,
            "win_probability": metrics.home_win_probability if is_home else metrics.away_win_probability,
            "possession": metrics.home_possession if is_home else metrics.away_possession,
            "shots": metrics.home_shots if is_home else metrics.away_shots,
            "shots_on_target": metrics.home_shots_on_target if is_home else metrics.away_shots_on_target
        }
    
    def evaluate_advanced_condition(self, metrics: MatchMetrics, condition: str, team_name: str) -> Tuple[bool, str]:
        """Evaluate advanced alert conditions"""
        team_metrics = self.get_team_metrics(metrics, team_name)
        
        # Parse condition (simplified for now)
        condition = condition.lower()
        
        if "xg" in condition and ">" in condition:
            threshold = float(condition.split(">")[1].strip())
            if team_metrics["xg"] > threshold:
                return True, f"{team_name} xG: {team_metrics['xg']:.2f} > {threshold}"
        
        elif "momentum" in condition and ">" in condition:
            threshold = float(condition.split(">")[1].strip())
            if team_metrics["momentum"] > threshold:
                return True, f"{team_name} momentum: {team_metrics['momentum']:.1f} > {threshold}"
        
        elif "pressure" in condition and ">" in condition:
            threshold = float(condition.split(">")[1].strip())
            if team_metrics["pressure_index"] > threshold:
                return True, f"{team_name} pressure: {team_metrics['pressure_index']:.2f} > {threshold}"
        
        elif "win_probability" in condition and ">" in condition:
            threshold = float(condition.split(">")[1].strip())
            if team_metrics["win_probability"] > threshold:
                return True, f"{team_name} win probability: {team_metrics['win_probability']:.1%} > {threshold:.1%}"
        
        return False, ""

# Global instance
metrics_calculator = MetricsCalculator() 