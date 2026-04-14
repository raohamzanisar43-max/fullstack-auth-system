import sys
import os

# Set up paths to import the app
sys.path.append(os.path.join(os.getcwd(), 'tracify_backend', 'backend'))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.api_key import APIKey
from app.models.credit import CreditBalance, CreditTransaction, CreditPackage
from app.models.trace import TraceJob, ManualSearch, TraceResult, PropertyRecord
from app.models.dnc import DncScrubJob, DncScrubResult, DncRecord
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def register():
    email = "raohamzanisar43@gmail.com"
    username = "raohamza"
    password = "String123" # Must contain Upper, Lower, and Digit
    
    print(f"Attempting to register user: {email}...")
    
    try:
        db = SessionLocal()
        user_service = UserService(db)
        
        # Check if user already exists
        existing_user = user_service.get_user_by_email(email)
        if existing_user:
            print(f"⚠️  User {email} already exists!")
            db.close()
            return
        
        # Create user
        user_data = UserCreate(
            email=email,
            username=username,
            full_name="Rao Hamza",
            password=password,
            phone="03236878949",
            company="Tracerfy",
        )
        
        user = user_service.create_user(user_data)
        print(f"[SUCCESS] User registered successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: {password}")
        
        db.close()
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    register()
