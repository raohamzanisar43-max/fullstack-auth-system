"""
User service for handling user operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword, UserAdminUpdate
from app.core.security import get_password_hash, verify_password, generate_password_reset_token, verify_password_reset_token
from app.core.exceptions import ValidationError, NotFoundError, AuthenticationError


class UserService:
    """Service for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise ValidationError("User with this email already exists")
        
        if self.get_user_by_username(user_data.username):
            raise ValidationError("User with this username already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            phone=user_data.phone,
            company=user_data.company,
            bio=user_data.bio,
            is_active=True,
            is_verified=False,
            role="user"
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user profile"""
        user = self.get_user_by_id(user_id)
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_user_password(self, user_id: int, password_data: UserUpdatePassword) -> User:
        """Update user password"""
        user = self.get_user_by_id(user_id)
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        
        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def update_last_login(self, user_id: int) -> None:
        """Update user's last login time"""
        user = self.get_user_by_id(user_id)
        user.last_login = datetime.utcnow()
        self.db.commit()
    
    def change_user_status(self, user_id: int, is_active: bool) -> User:
        """Change user active status"""
        user = self.get_user_by_id(user_id)
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def admin_update_user(self, user_id: int, user_data: UserAdminUpdate) -> User:
        """Admin update user"""
        user = self.get_user_by_id(user_id)
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
        return True
    
    def get_users_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Get list of users with pagination and filtering"""
        query = self.db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def create_password_reset_token(self, email: str) -> str:
        """Create password reset token for user"""
        user = self.get_user_by_email(email)
        
        if not user:
            raise NotFoundError("User with this email not found")
        
        # Generate reset token
        reset_token = generate_password_reset_token(email)
        
        # Save token to user
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        self.db.commit()
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> User:
        """Reset user password using token"""
        # Verify token
        email = verify_password_reset_token(token)
        
        if not email:
            raise ValidationError("Invalid or expired reset token")
        
        user = self.get_user_by_email(email)
        
        if not user or user.reset_token != token or user.reset_token_expires < datetime.utcnow():
            raise ValidationError("Invalid or expired reset token")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def verify_email(self, token: str) -> User:
        """Verify user email"""
        user = self.db.query(User).filter(User.verification_token == token).first()
        
        if not user:
            raise ValidationError("Invalid verification token")
        
        user.is_verified = True
        user.verification_token = None
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_verification_token(self, user_id: int) -> str:
        """Create email verification token"""
        user = self.get_user_by_id(user_id)
        
        if user.is_verified:
            raise ValidationError("Email is already verified")
        
        # Generate verification token
        from app.core.security import generate_secure_token
        verification_token = generate_secure_token(32)
        
        user.verification_token = verification_token
        
        self.db.commit()
        
        return verification_token


class APIKeyService:
    """Service for API key operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_api_key(self, user_id: int, key_data: dict) -> tuple[APIKey, str]:
        """Create new API key"""
        from app.core.security import generate_api_key, hash_api_key
        import json
        
        # Generate API key
        api_key, key_hash = generate_api_key()
        
        # Create API key record
        db_api_key = APIKey(
            name=key_data["name"],
            key_hash=key_hash,
            user_id=user_id,
            permissions=json.dumps(key_data.get("permissions", [])),
            rate_limit=key_data.get("rate_limit", 1000),
            allowed_ips=json.dumps(key_data.get("allowed_ips", [])),
            expires_at=key_data.get("expires_at"),
            is_active=True
        )
        
        self.db.add(db_api_key)
        self.db.commit()
        self.db.refresh(db_api_key)
        
        return db_api_key, api_key
    
    def get_user_api_keys(self, user_id: int, skip: int = 0, limit: int = 100) -> List[APIKey]:
        """Get user's API keys"""
        return self.db.query(APIKey).filter(APIKey.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_api_key_by_id(self, api_key_id: int, user_id: int) -> Optional[APIKey]:
        """Get API key by ID"""
        api_key = self.db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()
        
        if not api_key:
            raise NotFoundError("API key not found")
        
        return api_key
    
    def update_api_key(self, api_key_id: int, user_id: int, update_data: dict) -> APIKey:
        """Update API key"""
        api_key = self.get_api_key_by_id(api_key_id, user_id)
        import json
        
        # Update fields
        for field, value in update_data.items():
            if field in ["permissions", "allowed_ips"]:
                setattr(api_key, field, json.dumps(value))
            else:
                setattr(api_key, field, value)
        
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key
    
    def delete_api_key(self, api_key_id: int, user_id: int) -> bool:
        """Delete API key"""
        api_key = self.get_api_key_by_id(api_key_id, user_id)
        self.db.delete(api_key)
        self.db.commit()
        return True
    
    def update_api_key_usage(self, api_key_hash: str) -> None:
        """Update API key usage statistics"""
        api_key = self.db.query(APIKey).filter(APIKey.key_hash == api_key_hash).first()
        
        if api_key:
            api_key.last_used = datetime.utcnow()
            api_key.usage_count += 1
            self.db.commit()
