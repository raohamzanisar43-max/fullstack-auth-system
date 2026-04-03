import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tracify_backend', 'backend'))

from app.services.user_service import UserService
from app.schemas.user import UserRegister
from app.db.session import SessionLocal
from app.core.exceptions import ValidationError

# Test data
test_user_data = {
    "email": "Hamza@gmail.com",
    "username": "hamza", 
    "full_name": "rao Hamza",
    "phone": "03236878949",
    "company": "mars",
    "bio": "rao",
    "password": "String123",
    "confirm_password": "String123"
}

print("Testing registration...")

try:
    # Create schema
    user_schema = UserRegister(**test_user_data)
    print("OK Schema validation passed")
    
    # Get database session
    db = SessionLocal()
    print("OK Database session created")
    
    # Create user service
    user_service = UserService(db)
    print("OK User service created")
    
    # Try to create user
    user = user_service.create_user(user_schema)
    print(f"OK User created successfully: {user.email}")
    
    db.close()
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
