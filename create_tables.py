import sys
import os

# Set up paths to import the app
sys.path.append(os.path.join(os.getcwd(), 'tracify_backend', 'backend'))

from app.db.session import engine
from app.db.base import Base

def init_db():
    print("Creating all tables in PostgreSQL...")
    try:
        # This will create all tables defined in models that are imported in app.db.base
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All tables created successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {str(e)}")

if __name__ == "__main__":
    init_db()
