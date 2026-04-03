"""
User schemas for Pydantic validation and serialization
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None


class UserUpdatePassword(BaseModel):
    """User password update schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# Authentication schemas
class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserRegister(UserCreate):
    """User registration schema"""
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


# Token schemas
class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


# Password reset schemas
class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# Response schemas
class User(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserWithTokens(User):
    """User schema with tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# API Key schemas
class APIKeyBase(BaseModel):
    """Base API key schema"""
    name: str = Field(..., min_length=1, max_length=255)
    permissions: List[str] = []
    rate_limit: int = Field(default=1000, ge=1, le=10000)
    allowed_ips: List[str] = []
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    """API key creation schema"""
    pass


class APIKeyUpdate(BaseModel):
    """API key update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    permissions: Optional[List[str]] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=10000)
    allowed_ips: Optional[List[str]] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class APIKey(APIKeyBase):
    """API key response schema"""
    id: int
    user_id: int
    is_active: bool
    last_used: Optional[datetime] = None
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class APIKeyWithKey(APIKey):
    """API key response with actual key (only returned on creation)"""
    api_key: str


# Admin schemas
class UserAdminUpdate(BaseModel):
    """Admin user update schema"""
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[str] = None


class UserList(BaseModel):
    """User list response schema"""
    users: List[User]
    total: int
    page: int
    per_page: int
    pages: int


# Verification schemas
class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str


class ResendVerification(BaseModel):
    """Resend verification schema"""
    email: EmailStr
