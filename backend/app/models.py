from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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