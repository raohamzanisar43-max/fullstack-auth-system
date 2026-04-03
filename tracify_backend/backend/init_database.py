"""
Initialize database tables for Tracerfy Backend
"""

from app.db.session import engine, Base
from app.models.user import User
from app.models.api_key import APIKey

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
