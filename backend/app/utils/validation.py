"""
Data validation utilities for TouchLine application
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from ..core.exceptions import ValidationError

class DataValidator:
    """Comprehensive data validation utility"""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> None:
        """Validate that all required fields are present"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field_errors={field: "Required" for field in missing_fields}
            )
    
    @staticmethod
    def validate_string_field(value: Any, field_name: str, max_length: int = None, min_length: int = None, pattern: str = None) -> str:
        """Validate and sanitize string fields"""
        if value is None:
            raise ValidationError(f"Field '{field_name}' cannot be null", field=field_name, value=value)
        
        # Convert to string if needed
        if not isinstance(value, str):
            value = str(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Check length constraints
        if min_length and len(value) < min_length:
            raise ValidationError(f"Field '{field_name}' minimum length is {min_length} characters", field=field_name, value=value)
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"Field '{field_name}' maximum length is {max_length} characters", field=field_name, value=value)
        
        # Check pattern if provided
        if pattern and not re.match(pattern, value):
            raise ValidationError(f"Field '{field_name}' does not match pattern: {pattern}", field=field_name, value=value)
        
        return value
    
    @staticmethod
    def validate_integer_field(value: Any, field_name: str, min_value: int = None, max_value: int = None) -> int:
        """Validate and convert integer fields"""
        if value is None:
            raise ValidationError(f"Field '{field_name}' cannot be null", field=field_name, value=value)
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Field '{field_name}' must be a valid integer", field=field_name, value=value)
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"Field '{field_name}' must be at least {min_value}", field=field_name, value=int_value)
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"Field '{field_name}' must be at most {max_value}", field=field_name, value=int_value)
        
        return int_value
    
    @staticmethod
    def validate_float_field(value: Any, field_name: str, min_value: float = None, max_value: float = None) -> float:
        """Validate and convert float fields"""
        if value is None:
            raise ValidationError(f"Field '{field_name}' cannot be null", field=field_name, value=value)
        
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Field '{field_name}' must be a valid number", field=field_name, value=value)
        
        if min_value is not None and float_value < min_value:
            raise ValidationError(f"Field '{field_name}' must be at least {min_value}", field=field_name, value=float_value)
        
        if max_value is not None and float_value > max_value:
            raise ValidationError(f"Field '{field_name}' must be at most {max_value}", field=field_name, value=float_value)
        
        return float_value
    
    @staticmethod
    def validate_boolean_field(value: Any, field_name: str) -> bool:
        """Validate and convert boolean fields"""
        if value is None:
            raise ValidationError(f"Field '{field_name}' cannot be null", field=field_name, value=value)
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ('true', '1', 'yes', 'on'):
                return True
            elif value_lower in ('false', '0', 'no', 'off'):
                return False
        
        if isinstance(value, int):
            return bool(value)
        
        raise ValidationError(f"Field '{field_name}' must be a valid boolean", field=field_name, value=value)
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email = DataValidator.validate_string_field(email, "email", max_length=254)
        
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format", field="email", value=email)
        
        return email.lower()
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """Validate and format phone number"""
        phone = DataValidator.validate_string_field(phone, "phone_number", max_length=20)
        
        # If it already starts with +, validate the digits after +
        if phone.startswith('+'):
            digits_only = re.sub(r'\D', '', phone[1:])  # Remove + and non-digits
            if len(digits_only) < 7 or len(digits_only) > 15:
                raise ValidationError("Invalid phone number length", field="phone_number", value=phone)
            return phone  # Return as is if valid
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid phone number (7-15 digits)
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValidationError("Invalid phone number length", field="phone_number", value=phone)
        
        # Format as international format
        if len(digits_only) == 10:
            return f"+1{digits_only}"  # Assume US number
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return f"+{digits_only}"
        elif len(digits_only) > 11:
            return f"+{digits_only}"
        else:
            return f"+{digits_only}"
    
    @staticmethod
    def validate_team_name(team_name: str) -> str:
        """Validate and sanitize team name"""
        team_name = DataValidator.validate_string_field(
            team_name, 
            "team_name", 
            max_length=100, 
            min_length=2
        )
        
        # Remove excessive whitespace and normalize
        team_name = re.sub(r'\s+', ' ', team_name)
        
        # Check for common invalid characters
        invalid_chars = re.findall(r'[<>"\']', team_name)
        if invalid_chars:
            raise ValidationError(f"Contains invalid characters: {invalid_chars}", field="team_name", value=team_name)
        
        return team_name
    
    @staticmethod
    def validate_player_name(player_name: str) -> str:
        """Validate and sanitize player name"""
        player_name = DataValidator.validate_string_field(
            player_name, 
            "player_name", 
            max_length=100, 
            min_length=2
        )
        
        # Remove excessive whitespace and normalize
        player_name = re.sub(r'\s+', ' ', player_name)
        
        # Check for common invalid characters
        invalid_chars = re.findall(r'[<>"\']', player_name)
        if invalid_chars:
            raise ValidationError(f"Contains invalid characters: {invalid_chars}", field="player_name", value=player_name)
        
        return player_name
    
    @staticmethod
    def validate_match_data(match_data: Dict) -> Dict:
        """Validate match data structure"""
        required_fields = ['fixture', 'teams', 'goals', 'league']
        DataValidator.validate_required_fields(match_data, required_fields)
        
        # Validate fixture data
        if 'fixture' in match_data:
            fixture = match_data['fixture']
            if not isinstance(fixture, dict):
                raise ValidationError("fixture", fixture, "Fixture must be an object")
            
            if 'id' in fixture:
                fixture['id'] = DataValidator.validate_integer_field(fixture['id'], "fixture.id", min_value=1)
        
        # Validate teams data
        if 'teams' in match_data:
            teams = match_data['teams']
            if not isinstance(teams, dict):
                raise ValidationError("teams", teams, "Teams must be an object")
            
            for team_type in ['home', 'away']:
                if team_type in teams:
                    team = teams[team_type]
                    if isinstance(team, dict) and 'name' in team:
                        team['name'] = DataValidator.validate_team_name(team['name'])
        
        # Validate goals data
        if 'goals' in match_data:
            goals = match_data['goals']
            if not isinstance(goals, dict):
                raise ValidationError("goals", goals, "Goals must be an object")
            
            for goal_type in ['home', 'away']:
                if goal_type in goals:
                    goals[goal_type] = DataValidator.validate_integer_field(
                        goals[goal_type], 
                        f"goals.{goal_type}", 
                        min_value=0
                    )
        
        return match_data
    
    @staticmethod
    def validate_alert_condition(condition_data: Dict) -> Dict:
        """Validate alert condition data"""
        required_fields = ['alert_type', 'team', 'threshold']
        DataValidator.validate_required_fields(condition_data, required_fields)
        
        # Validate alert type
        valid_alert_types = [
            'goals', 'score_difference', 'possession', 'time_based', 'cards',
            'xg', 'momentum', 'pressure', 'win_probability', 'custom',
            'player_goals', 'player_assists', 'player_cards', 'player_shots',
            'player_passes', 'player_tackles', 'player_rating', 'player_minutes',
            'player_goal_contributions'
        ]
        
        alert_type = DataValidator.validate_string_field(condition_data['alert_type'], "alert_type")
        if alert_type not in valid_alert_types:
            raise ValidationError("alert_type", alert_type, f"Invalid alert type. Must be one of: {', '.join(valid_alert_types)}")
        
        # Validate team name
        condition_data['team'] = DataValidator.validate_team_name(condition_data['team'])
        
        # Validate threshold
        condition_data['threshold'] = DataValidator.validate_float_field(
            condition_data['threshold'], 
            "threshold", 
            min_value=0.0
        )
        
        # Validate player data if it's a player-specific alert
        if alert_type.startswith('player_'):
            if 'player_name' in condition_data and condition_data['player_name']:
                condition_data['player_name'] = DataValidator.validate_player_name(condition_data['player_name'])
            
            if 'player_id' in condition_data and condition_data['player_id']:
                condition_data['player_id'] = DataValidator.validate_integer_field(
                    condition_data['player_id'], 
                    "player_id", 
                    min_value=1
                )
        
        return condition_data
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove potentially dangerous HTML/script content"""
        if not text:
            return text
        
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove other potentially dangerous tags
        dangerous_tags = ['iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select']
        for tag in dangerous_tags:
            text = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(rf'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
        
        # Remove onclick and other event handlers
        text = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        
        # Remove javascript: URLs
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str, max_days: int = 30) -> tuple[str, str]:
        """Validate date range"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValidationError("date_range", f"{start_date} to {end_date}", f"Invalid date format: {e}")
        
        if start >= end:
            raise ValidationError("date_range", f"{start_date} to {end_date}", "Start date must be before end date")
        
        if (end - start).days > max_days:
            raise ValidationError("date_range", f"{start_date} to {end_date}", f"Date range cannot exceed {max_days} days")
        
        return start_date, end_date

# Global validator instance
validator = DataValidator() 