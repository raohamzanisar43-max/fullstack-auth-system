"""
User model for Tracerfy Backend
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="user")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Profile fields
    phone = Column(String(20), nullable=True)
    company = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Email verification
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    
    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
