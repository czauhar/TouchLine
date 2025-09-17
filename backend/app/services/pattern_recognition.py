"""
TouchLine Pattern Recognition Service
Identifies and alerts on complex game patterns and sequences
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types of patterns that can be recognized"""
    GOAL_SEQUENCE = "goal_sequence"
    CARD_SEQUENCE = "card_sequence"
    POSSESSION_SWING = "possession_swing"
    MOMENTUM_SHIFT = "momentum_shift"
    PRESSURE_BUILDUP = "pressure_buildup"
    TIME_BASED_PATTERN = "time_based_pattern"
    PLAYER_PERFORMANCE = "player_performance"
    TEAM_FORMATION = "team_formation"
    SET_PIECE_PATTERN = "set_piece_pattern"
    COUNTER_ATTACK = "counter_attack"

class PatternSeverity(Enum):
    """Severity levels for patterns"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PatternEvent:
    """Individual event in a pattern"""
    event_type: str
    timestamp: datetime
    team: str
    player: Optional[str] = None
    value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GamePattern:
    """A recognized game pattern"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    severity: PatternSeverity
    events: List[PatternEvent] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> timedelta:
        """Duration of the pattern"""
        end = self.end_time or datetime.utcnow()
        return end - self.start_time
    
    @property
    def event_count(self) -> int:
        """Number of events in the pattern"""
        return len(self.events)

class PatternDetector:
    """Detects specific types of patterns"""
    
    def __init__(self):
        self.pattern_history = defaultdict(list)  # fixture_id -> patterns
        self.event_buffer = defaultdict(deque)  # fixture_id -> recent events
        self.buffer_size = 50  # Keep last 50 events per match
    
    def detect_patterns(self, match_data, fixture_id: str) -> List[GamePattern]:
        """Detect all patterns in the current match state"""
        patterns = []
        
        # Add current match state to event buffer
        self._add_match_to_buffer(match_data, fixture_id)
        
        # Detect different types of patterns
        patterns.extend(self._detect_goal_sequences(fixture_id))
        patterns.extend(self._detect_card_sequences(fixture_id))
        patterns.extend(self._detect_possession_swings(fixture_id))
        patterns.extend(self._detect_momentum_shifts(fixture_id))
        patterns.extend(self._detect_pressure_buildups(fixture_id))
        patterns.extend(self._detect_time_based_patterns(fixture_id))
        
        # Store detected patterns
        for pattern in patterns:
            self.pattern_history[fixture_id].append(pattern)
        
        return patterns
    
    def _add_match_to_buffer(self, match_data, fixture_id: str):
        """Add current match state to event buffer"""
        current_time = datetime.utcnow()
        
        # Extract basic events from match data
        if hasattr(match_data, 'home_team'):  # MatchData object
            # Goals
            if match_data.home_score > 0:
                self.event_buffer[fixture_id].append(PatternEvent(
                    event_type="goal",
                    timestamp=current_time,
                    team=match_data.home_team,
                    value=match_data.home_score
                ))
            
            if match_data.away_score > 0:
                self.event_buffer[fixture_id].append(PatternEvent(
                    event_type="goal",
                    timestamp=current_time,
                    team=match_data.away_team,
                    value=match_data.away_score
                ))
            
            # Cards
            if match_data.home_yellow_cards > 0:
                self.event_buffer[fixture_id].append(PatternEvent(
                    event_type="yellow_card",
                    timestamp=current_time,
                    team=match_data.home_team,
                    value=match_data.home_yellow_cards
                ))
            
            if match_data.away_yellow_cards > 0:
                self.event_buffer[fixture_id].append(PatternEvent(
                    event_type="yellow_card",
                    timestamp=current_time,
                    team=match_data.away_team,
                    value=match_data.away_yellow_cards
                ))
            
            if match_data.home_red_cards > 0:
                self.event_buffer[fixture_id].append(PatternEvent(
                    event_type="red_card",
                    timestamp=current_time,
                    team=match_data.home_team,
                    value=match_data.home_red_cards
                ))
            
            if match_data.away_red_cards > 0:
                self.event_buffer[fixture_id].append(PatternEvent(
                    event_type="red_card",
                    timestamp=current_time,
                    team=match_data.away_team,
                    value=match_data.away_red_cards
                ))
            
            # Possession
            self.event_buffer[fixture_id].append(PatternEvent(
                event_type="possession",
                timestamp=current_time,
                team=match_data.home_team,
                value=match_data.home_possession
            ))
            
            self.event_buffer[fixture_id].append(PatternEvent(
                event_type="possession",
                timestamp=current_time,
                team=match_data.away_team,
                value=match_data.away_possession
            ))
            
            # Momentum
            self.event_buffer[fixture_id].append(PatternEvent(
                event_type="momentum",
                timestamp=current_time,
                team=match_data.home_team,
                value=match_data.home_momentum
            ))
            
            self.event_buffer[fixture_id].append(PatternEvent(
                event_type="momentum",
                timestamp=current_time,
                team=match_data.away_team,
                value=match_data.away_momentum
            ))
            
            # Pressure
            self.event_buffer[fixture_id].append(PatternEvent(
                event_type="pressure",
                timestamp=current_time,
                team=match_data.home_team,
                value=match_data.home_pressure
            ))
            
            self.event_buffer[fixture_id].append(PatternEvent(
                event_type="pressure",
                timestamp=current_time,
                team=match_data.away_team,
                value=match_data.away_pressure
            ))
        
        # Limit buffer size
        while len(self.event_buffer[fixture_id]) > self.buffer_size:
            self.event_buffer[fixture_id].popleft()
    
    def _detect_goal_sequences(self, fixture_id: str) -> List[GamePattern]:
        """Detect rapid goal sequences"""
        patterns = []
        events = list(self.event_buffer[fixture_id])
        goal_events = [e for e in events if e.event_type == "goal"]
        
        if len(goal_events) >= 2:
            # Check for rapid goals (within 5 minutes)
            for i in range(len(goal_events) - 1):
                time_diff = (goal_events[i + 1].timestamp - goal_events[i].timestamp).total_seconds()
                if time_diff <= 300:  # 5 minutes
                    pattern = GamePattern(
                        pattern_id=f"goal_sequence_{fixture_id}_{i}",
                        pattern_type=PatternType.GOAL_SEQUENCE,
                        name="Rapid Goal Sequence",
                        description=f"Two goals within {time_diff/60:.1f} minutes",
                        severity=PatternSeverity.HIGH if time_diff <= 120 else PatternSeverity.MEDIUM,
                        events=goal_events[i:i+2],
                        start_time=goal_events[i].timestamp,
                        end_time=goal_events[i + 1].timestamp,
                        confidence=0.9,
                        metadata={"time_gap": time_diff}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_card_sequences(self, fixture_id: str) -> List[GamePattern]:
        """Detect card sequences indicating aggressive play"""
        patterns = []
        events = list(self.event_buffer[fixture_id])
        card_events = [e for e in events if e.event_type in ["yellow_card", "red_card"]]
        
        if len(card_events) >= 3:
            # Check for rapid cards (within 10 minutes)
            for i in range(len(card_events) - 2):
                time_diff = (card_events[i + 2].timestamp - card_events[i].timestamp).total_seconds()
                if time_diff <= 600:  # 10 minutes
                    pattern = GamePattern(
                        pattern_id=f"card_sequence_{fixture_id}_{i}",
                        pattern_type=PatternType.CARD_SEQUENCE,
                        name="Aggressive Play Pattern",
                        description=f"Three cards within {time_diff/60:.1f} minutes",
                        severity=PatternSeverity.MEDIUM,
                        events=card_events[i:i+3],
                        start_time=card_events[i].timestamp,
                        end_time=card_events[i + 2].timestamp,
                        confidence=0.8,
                        metadata={"time_gap": time_diff}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_possession_swings(self, fixture_id: str) -> List[GamePattern]:
        """Detect significant possession swings"""
        patterns = []
        events = list(self.event_buffer[fixture_id])
        possession_events = [e for e in events if e.event_type == "possession"]
        
        if len(possession_events) >= 4:
            # Group by team
            home_possession = [e for e in possession_events if "home" in e.team.lower()]
            away_possession = [e for e in possession_events if "away" in e.team.lower()]
            
            if len(home_possession) >= 2 and len(away_possession) >= 2:
                # Check for significant swings (>20% change)
                home_swing = abs(home_possession[-1].value - home_possession[0].value)
                away_swing = abs(away_possession[-1].value - away_possession[0].value)
                
                if home_swing > 20 or away_swing > 20:
                    pattern = GamePattern(
                        pattern_id=f"possession_swing_{fixture_id}",
                        pattern_type=PatternType.POSSESSION_SWING,
                        name="Significant Possession Swing",
                        description=f"Possession changed by {max(home_swing, away_swing):.1f}%",
                        severity=PatternSeverity.MEDIUM,
                        events=possession_events[-4:],
                        start_time=possession_events[0].timestamp,
                        end_time=possession_events[-1].timestamp,
                        confidence=0.7,
                        metadata={"home_swing": home_swing, "away_swing": away_swing}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_momentum_shifts(self, fixture_id: str) -> List[GamePattern]:
        """Detect momentum shifts in the game"""
        patterns = []
        events = list(self.event_buffer[fixture_id])
        momentum_events = [e for e in events if e.event_type == "momentum"]
        
        if len(momentum_events) >= 4:
            # Group by team
            home_momentum = [e for e in momentum_events if "home" in e.team.lower()]
            away_momentum = [e for e in momentum_events if "away" in e.team.lower()]
            
            if len(home_momentum) >= 2 and len(away_momentum) >= 2:
                # Check for significant momentum shifts (>30 points)
                home_shift = abs(home_momentum[-1].value - home_momentum[0].value)
                away_shift = abs(away_momentum[-1].value - away_momentum[0].value)
                
                if home_shift > 30 or away_shift > 30:
                    pattern = GamePattern(
                        pattern_id=f"momentum_shift_{fixture_id}",
                        pattern_type=PatternType.MOMENTUM_SHIFT,
                        name="Momentum Shift",
                        description=f"Momentum changed by {max(home_shift, away_shift):.1f} points",
                        severity=PatternSeverity.HIGH,
                        events=momentum_events[-4:],
                        start_time=momentum_events[0].timestamp,
                        end_time=momentum_events[-1].timestamp,
                        confidence=0.8,
                        metadata={"home_shift": home_shift, "away_shift": away_shift}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_pressure_buildups(self, fixture_id: str) -> List[GamePattern]:
        """Detect pressure buildups"""
        patterns = []
        events = list(self.event_buffer[fixture_id])
        pressure_events = [e for e in events if e.event_type == "pressure"]
        
        if len(pressure_events) >= 4:
            # Group by team
            home_pressure = [e for e in pressure_events if "home" in e.team.lower()]
            away_pressure = [e for e in pressure_events if "away" in e.team.lower()]
            
            if len(home_pressure) >= 2 and len(away_pressure) >= 2:
                # Check for sustained high pressure (>70)
                home_high_pressure = all(e.value > 70 for e in home_pressure[-2:])
                away_high_pressure = all(e.value > 70 for e in away_pressure[-2:])
                
                if home_high_pressure or away_high_pressure:
                    pattern = GamePattern(
                        pattern_id=f"pressure_buildup_{fixture_id}",
                        pattern_type=PatternType.PRESSURE_BUILDUP,
                        name="High Pressure Buildup",
                        description="Sustained high pressure detected",
                        severity=PatternSeverity.MEDIUM,
                        events=pressure_events[-4:],
                        start_time=pressure_events[0].timestamp,
                        end_time=pressure_events[-1].timestamp,
                        confidence=0.7,
                        metadata={"home_high": home_high_pressure, "away_high": away_high_pressure}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_time_based_patterns(self, fixture_id: str) -> List[GamePattern]:
        """Detect time-based patterns (e.g., late goals, early cards)"""
        patterns = []
        events = list(self.event_buffer[fixture_id])
        
        # Late goals (after 80 minutes)
        goal_events = [e for e in events if e.event_type == "goal"]
        late_goals = [e for e in goal_events if e.timestamp.minute >= 80]
        
        if len(late_goals) >= 2:
            pattern = GamePattern(
                pattern_id=f"late_goals_{fixture_id}",
                pattern_type=PatternType.TIME_BASED_PATTERN,
                name="Late Goal Pattern",
                description="Multiple goals in final 10 minutes",
                severity=PatternSeverity.HIGH,
                events=late_goals,
                start_time=late_goals[0].timestamp,
                end_time=late_goals[-1].timestamp,
                confidence=0.8,
                metadata={"time_period": "late"}
            )
            patterns.append(pattern)
        
        # Early cards (first 20 minutes)
        card_events = [e for e in events if e.event_type in ["yellow_card", "red_card"]]
        early_cards = [e for e in card_events if e.timestamp.minute <= 20]
        
        if len(early_cards) >= 2:
            pattern = GamePattern(
                pattern_id=f"early_cards_{fixture_id}",
                pattern_type=PatternType.TIME_BASED_PATTERN,
                name="Early Aggression Pattern",
                description="Multiple cards in first 20 minutes",
                severity=PatternSeverity.MEDIUM,
                events=early_cards,
                start_time=early_cards[0].timestamp,
                end_time=early_cards[-1].timestamp,
                confidence=0.7,
                metadata={"time_period": "early"}
            )
            patterns.append(pattern)
        
        return patterns

class PatternRecognitionService:
    """Service for managing pattern recognition"""
    
    def __init__(self):
        self.detector = PatternDetector()
        self.active_patterns = {}  # fixture_id -> active patterns
        self.pattern_alerts = {}  # pattern_type -> alert_config
    
    def analyze_match(self, match_data, fixture_id: str) -> List[GamePattern]:
        """Analyze a match for patterns"""
        try:
            patterns = self.detector.detect_patterns(match_data, fixture_id)
            
            # Update active patterns
            if fixture_id not in self.active_patterns:
                self.active_patterns[fixture_id] = []
            
            self.active_patterns[fixture_id].extend(patterns)
            
            # Clean up old patterns (older than 2 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=2)
            self.active_patterns[fixture_id] = [
                p for p in self.active_patterns[fixture_id]
                if p.start_time > cutoff_time
            ]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for match {fixture_id}: {e}")
            return []
    
    def get_match_patterns(self, fixture_id: str) -> List[GamePattern]:
        """Get all patterns for a specific match"""
        return self.active_patterns.get(fixture_id, [])
    
    def get_patterns_by_type(self, pattern_type: PatternType) -> List[GamePattern]:
        """Get all patterns of a specific type"""
        all_patterns = []
        for patterns in self.active_patterns.values():
            all_patterns.extend([p for p in patterns if p.pattern_type == pattern_type])
        return all_patterns
    
    def get_high_severity_patterns(self) -> List[GamePattern]:
        """Get all high and critical severity patterns"""
        all_patterns = []
        for patterns in self.active_patterns.values():
            all_patterns.extend([
                p for p in patterns 
                if p.severity in [PatternSeverity.HIGH, PatternSeverity.CRITICAL]
            ])
        return all_patterns
    
    def configure_pattern_alert(self, pattern_type: PatternType, severity_threshold: PatternSeverity, 
                               enabled: bool = True):
        """Configure alerts for specific pattern types"""
        self.pattern_alerts[pattern_type] = {
            "severity_threshold": severity_threshold,
            "enabled": enabled
        }
    
    def should_alert_pattern(self, pattern: GamePattern) -> bool:
        """Check if a pattern should trigger an alert"""
        if pattern.pattern_type not in self.pattern_alerts:
            return False
        
        config = self.pattern_alerts[pattern.pattern_type]
        if not config["enabled"]:
            return False
        
        # Check severity threshold
        severity_order = [PatternSeverity.LOW, PatternSeverity.MEDIUM, PatternSeverity.HIGH, PatternSeverity.CRITICAL]
        pattern_severity_index = severity_order.index(pattern.severity)
        threshold_index = severity_order.index(config["severity_threshold"])
        
        return pattern_severity_index >= threshold_index

# Global instances
pattern_detector = PatternDetector()
pattern_recognition_service = PatternRecognitionService() 