"""
Database base configuration for Tracerfy Backend
"""

from app.db.session import Base

# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.api_key import APIKey

# Make sure all models are imported here so they get registered
__all__ = ["Base", "User", "APIKey"]
