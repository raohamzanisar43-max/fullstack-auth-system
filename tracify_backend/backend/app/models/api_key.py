"""
API Key model for Tracerfy Backend
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class APIKey(Base):
    """API Key model for API authentication"""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permissions and restrictions
    permissions = Column(Text, default="[]")  # JSON string of permissions
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    allowed_ips = Column(Text, default="[]")  # JSON string of allowed IPs
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.name}, user_id={self.user_id})>"
