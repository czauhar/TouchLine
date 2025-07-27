from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user")
    preferences = Column(Text, nullable=True)  # JSON as text
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    alerts = relationship("Alert", back_populates="user")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # ID from sports API
    home_team = Column(String)
    away_team = Column(String)
    league = Column(String)
    start_time = Column(DateTime)
    status = Column(String)  # live, finished, scheduled
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MatchCache(Base):
    """Cache for match data to reduce API calls"""
    __tablename__ = "match_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    match_data = Column(JSON)  # Full match data from API
    stats_data = Column(JSON, nullable=True)  # Statistics data
    events_data = Column(JSON, nullable=True)  # Events data
    lineups_data = Column(JSON, nullable=True)  # Lineups data
    alert_metrics = Column(JSON, nullable=True)  # Processed alert metrics
    last_updated = Column(DateTime, default=datetime.utcnow)
    cache_ttl = Column(Integer, default=300)  # Cache TTL in seconds (5 minutes)
    
    @property
    def is_expired(self):
        """Check if cache entry is expired"""
        return (datetime.utcnow() - self.last_updated).total_seconds() > self.cache_ttl

class MatchMetrics(Base):
    """Structured metrics for efficient alert processing"""
    __tablename__ = "match_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, index=True)  # External match ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Basic metrics
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    elapsed_time = Column(Integer, default=0)
    status = Column(String)
    
    # Possession and control
    home_possession = Column(Float, default=50.0)
    away_possession = Column(Float, default=50.0)
    
    # Attacking metrics
    home_shots = Column(Integer, default=0)
    away_shots = Column(Integer, default=0)
    home_shots_on_target = Column(Integer, default=0)
    away_shots_on_target = Column(Integer, default=0)
    home_corners = Column(Integer, default=0)
    away_corners = Column(Integer, default=0)
    
    # Defensive metrics
    home_fouls = Column(Integer, default=0)
    away_fouls = Column(Integer, default=0)
    home_yellow_cards = Column(Integer, default=0)
    away_yellow_cards = Column(Integer, default=0)
    home_red_cards = Column(Integer, default=0)
    away_red_cards = Column(Integer, default=0)
    
    # Advanced metrics
    home_xg = Column(Float, default=0.0)
    away_xg = Column(Float, default=0.0)
    home_pressure = Column(Float, default=0.0)
    away_pressure = Column(Float, default=0.0)
    home_momentum = Column(Float, default=0.0)
    away_momentum = Column(Float, default=0.0)
    
    # Additional context
    referee = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    weather = Column(JSON, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String)
    alert_type = Column(String)  # goals, xg, momentum, pressure, win_probability, etc.
    team = Column(String)  # team name for the alert
    condition = Column(String)  # condition description
    threshold = Column(Float)
    time_window = Column(Integer, nullable=True)  # minutes for time-based alerts
    user_phone = Column(String, nullable=True)  # phone number for SMS
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    trigger_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    conditions_json = Column(Text, nullable=True)  # Store full JSON for analytics
    
    # Player-specific fields
    player_id = Column(Integer, nullable=True)  # Player ID from sports API
    player_name = Column(String, nullable=True)  # Player name for display
    
    user = relationship("User", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert")

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    match_id = Column(String)  # external match ID from sports API
    triggered_at = Column(DateTime, default=datetime.utcnow)
    trigger_message = Column(Text)  # what triggered the alert
    sms_sent = Column(Boolean, default=False)
    sms_message_id = Column(String, nullable=True)  # Twilio message SID
    match_data = Column(Text, nullable=True)  # JSON string of match data
    
    alert = relationship("Alert", back_populates="history")

class PlayerStats(Base):
    """Player statistics tracking"""
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, index=True)  # External match ID
    player_id = Column(Integer, index=True)  # Player ID from sports API
    player_name = Column(String)
    team = Column(String)
    position = Column(String)
    
    # Performance stats
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    shots = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    passes = Column(Integer, default=0)
    passes_accurate = Column(Integer, default=0)
    tackles = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)
    fouls_drawn = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def pass_accuracy(self) -> float:
        """Calculate pass accuracy percentage"""
        return (self.passes_accurate / self.passes * 100) if self.passes > 0 else 0.0
    
    @property
    def goal_contributions(self) -> int:
        """Total goal contributions (goals + assists)"""
        return self.goals + self.assists