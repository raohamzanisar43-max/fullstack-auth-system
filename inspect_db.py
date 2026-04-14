import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "tracify_backend", "backend"))

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), "tracify_backend", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found in .env")
    sys.exit(1)

# Fix for windows sqlite path if needed
if DATABASE_URL.startswith("sqlite") and "///" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite:///")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    from app.models.user import User
    from app.models.trace import TraceJob, ManualSearch
    
    print("--- Users ---")
    users = db.query(User).all()
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Username: {u.username}")
        
    print("\n--- Trace Jobs ---")
    jobs = db.query(TraceJob).all()
    if not jobs:
        print("No trace jobs found.")
    for j in jobs:
        print(f"ID: {j.id}, User ID: {j.user_id}, Name: {j.name}, Status: {j.status}")
        
    print("\n--- Manual Searches ---")
    searches = db.query(ManualSearch).all()
    if not searches:
        print("No manual searches found.")
    for s in searches:
        print(f"ID: {s.id}, User ID: {s.user_id}, Type: {s.search_type}, Query: {s.search_query}")

finally:
    db.close()
