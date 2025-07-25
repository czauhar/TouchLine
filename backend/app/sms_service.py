import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from dotenv import load_dotenv
from .core.config import settings

load_dotenv()

class SMSService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.client = None
        self.is_configured = False
        
        if self.account_sid and self.auth_token and self.phone_number:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.is_configured = True
            except Exception as e:
                print(f"Failed to initialize Twilio client: {e}")
                self.is_configured = False
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS message"""
        if not self.is_configured:
            print("SMS service not configured")
            return False
            
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            print(f"SMS sent successfully: {message.sid}")
            return True
        except TwilioException as e:
            print(f"Failed to send SMS: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending SMS: {e}")
            return False
    
    def format_alert_message(self, alert_name: str, match_info: dict, condition_met: str) -> str:
        """Format alert message for SMS"""
        home_team = match_info.get("home_team", "Unknown")
        away_team = match_info.get("away_team", "Unknown")
        home_score = match_info.get("home_score", 0)
        away_score = match_info.get("away_score", 0)
        league = match_info.get("league", "Unknown")
        
        message = f"⚽ TouchLine Alert: {alert_name}\n"
        message += f"🏆 {league}\n"
        message += f"📊 {home_team} {home_score} - {away_score} {away_team}\n"
        message += f"🎯 {condition_met}\n"
        message += f"⏰ {match_info.get('elapsed', 'N/A')} min"
        
        return message
    
    def is_configured(self) -> bool:
        """Check if SMS service is properly configured"""
        return self.is_configured

# Global instance
sms_service = SMSService() 