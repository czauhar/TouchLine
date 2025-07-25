from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Alert schemas
class AlertBase(BaseModel):
    name: str
    team: str
    alert_type: str
    threshold: float
    description: Optional[str] = ""
    time_window: Optional[int] = None

class AlertCreate(AlertBase):
    user_phone: Optional[str] = None

class AlertUpdate(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    alert_type: Optional[str] = None
    threshold: Optional[float] = None
    description: Optional[str] = None
    time_window: Optional[int] = None
    is_active: Optional[bool] = None
    user_phone: Optional[str] = None

class AlertResponse(AlertBase):
    id: int
    user_id: Optional[int]
    condition: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Match schemas
class MatchBase(BaseModel):
    external_id: str
    home_team: str
    away_team: str
    league: str
    start_time: datetime
    status: str
    home_score: int = 0
    away_score: int = 0

class MatchResponse(MatchBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(UserCreate):
    pass

# API Response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# Alert History schemas
class AlertHistoryBase(BaseModel):
    alert_id: int
    match_id: str
    trigger_message: str
    sms_sent: bool
    match_data: Optional[str] = None

class AlertHistoryResponse(AlertHistoryBase):
    id: int
    triggered_at: datetime
    sms_message_id: Optional[str] = None
    
    class Config:
        from_attributes = True 