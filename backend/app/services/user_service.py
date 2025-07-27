from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import User
from ..utils.logger import log_database_operation
import time

class UserService:
    """Service for managing user data and operations"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        start_time = time.time()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            log_database_operation(
                "select", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "select", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        start_time = time.time()
        try:
            user = db.query(User).filter(User.email == email).first()
            
            log_database_operation(
                "select", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "select", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        start_time = time.time()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            log_database_operation(
                "select", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "select", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Create a new user"""
        start_time = time.time()
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            log_database_operation(
                "insert", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "insert", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
        """Update user data"""
        start_time = time.time()
        try:
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                log_database_operation(
                    "update", "users", False, time.time() - start_time, "User not found"
                )
                return None
            
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            
            log_database_operation(
                "update", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "update", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        start_time = time.time()
        try:
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                log_database_operation(
                    "delete", "users", False, time.time() - start_time, "User not found"
                )
                return False
            
            db.delete(user)
            db.commit()
            
            log_database_operation(
                "delete", "users", True, time.time() - start_time
            )
            return True
        except Exception as e:
            log_database_operation(
                "delete", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        start_time = time.time()
        try:
            users = db.query(User).offset(skip).limit(limit).all()
            
            log_database_operation(
                "select", "users", True, time.time() - start_time
            )
            return users
        except Exception as e:
            log_database_operation(
                "select", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_active_users(db: Session) -> List[User]:
        """Get all active users"""
        start_time = time.time()
        try:
            users = db.query(User).filter(User.is_active == True).all()
            
            log_database_operation(
                "select", "users", True, time.time() - start_time
            )
            return users
        except Exception as e:
            log_database_operation(
                "select", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """Deactivate a user"""
        start_time = time.time()
        try:
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                log_database_operation(
                    "update", "users", False, time.time() - start_time, "User not found"
                )
                return None
            
            user.is_active = False
            db.commit()
            db.refresh(user)
            
            log_database_operation(
                "update", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "update", "users", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> Optional[User]:
        """Activate a user"""
        start_time = time.time()
        try:
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                log_database_operation(
                    "update", "users", False, time.time() - start_time, "User not found"
                )
                return None
            
            user.is_active = True
            db.commit()
            db.refresh(user)
            
            log_database_operation(
                "update", "users", True, time.time() - start_time
            )
            return user
        except Exception as e:
            log_database_operation(
                "update", "users", False, time.time() - start_time, str(e)
            )
            raise 