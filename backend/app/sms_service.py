import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from dotenv import load_dotenv

load_dotenv()

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize Twilio client if credentials are available
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.is_configured = True
        else:
            self.client = None
            self.is_configured = False
    
    def send_alert(self, to_number: str, message: str) -> dict:
        """Send SMS alert"""
        if not self.is_configured:
            return {
                "success": False,
                "error": "SMS service not configured",
                "message": f"[SMS NOT SENT] {message}"
            }
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "message": message
            }
            
        except TwilioException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"[SMS FAILED] {message}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message": f"[SMS ERROR] {message}"
            }
    
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