import sys
import os

# Set up paths to import the app
sys.path.append(os.path.join(os.getcwd(), 'tracify_backend', 'backend'))

from app.db.session import SessionLocal, engine
from app.models.user import User
from sqlalchemy import text

def check_users():
    print("Checking database connection...")
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1')).scalar()
            print(f"[SUCCESS] Connection successful! (Result: {result})")
            
            # Check for users table
            print("\nChecking users table...")
            db = SessionLocal()
            users = db.query(User).all()
            
            if not users:
                print("[WARNING] No users found in the database. You need to register first.")
            else:
                print(f"[SUCCESS] Found {len(users)} users:")
                for user in users:
                    print(f"   - Email: {user.email}, Username: {user.username}, Active: {user.is_active}")
            
            db.close()
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        if "relation \"users\" does not exist" in str(e).lower():
            print("\n[TIP] The 'users' table doesn't exist. You might need to run migrations.")
            print("   Run: python start.py migrate")
        elif "password authentication failed" in str(e).lower():
            print("\n[TIP] Database password is incorrect in your .env file.")
        elif "could not connect to server" in str(e).lower():
            print("\n[TIP] PostgreSQL server is not running or host/port is wrong.")

if __name__ == "__main__":
    check_users()
