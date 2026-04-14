import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Set up paths to import the app
sys.path.append(os.path.join(os.getcwd(), 'tracify_backend', 'backend'))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.api_key import APIKey
from app.models.credit import CreditBalance, CreditTransaction, CreditTransactionType
from app.models.trace import TraceJob, ManualSearch, TraceResult, TraceJobStatus, TraceType, ManualSearchType
from app.models.dnc import DncScrubJob, DncScrubStatus

def seed_data():
    email = "raohamzanisar43@gmail.com"
    print(f"--- Seeding test data for {email} ---")
    
    db = SessionLocal()
    try:
        # 1. Get User
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"[ERROR] User {email} not found! Please register first.")
            return
        
        user_id = user.id
        print(f"Found User ID: {user_id}")

        # 2. Seed Credits
        print("Adding credits...")
        balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
        if not balance:
            balance = CreditBalance(
                user_id=user_id,
                current_credits=0,
                total_purchased=0,
                total_used=0,
                total_bonus=0,
                effective_rate=0.02
            )
            db.add(balance)
            db.flush()
        
        amount = 10000
        balance.current_credits += amount
        balance.total_bonus += amount
        balance.last_updated = datetime.utcnow()
        
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.BONUS,
            amount=amount,
            balance_after=balance.current_credits,
            description="Integration test bonus credits",
            created_at=datetime.utcnow()
        )
        db.add(transaction)
        print(f"Added {amount} credits. New balance: {balance.current_credits}")

        # 3. Seed Trace Jobs
        print("Adding trace jobs...")
        # Clean up existing test jobs for this user to avoid clutter
        # db.query(TraceJob).filter(TraceJob.user_id == user_id).delete()
        
        jobs_to_create = [
            {"name": "Texas Property Owners", "type": TraceType.NORMAL, "status": TraceJobStatus.COMPLETED, "records": 1250, "days_ago": 5},
            {"name": "Florida Distressed Leads", "type": TraceType.ENHANCED, "status": TraceJobStatus.COMPLETED, "records": 450, "days_ago": 3},
            {"name": "California Investor List", "type": TraceType.NORMAL, "status": TraceJobStatus.PROCESSING, "records": 2500, "days_ago": 1},
            {"name": "NY Multi-Family Owners", "type": TraceType.ENHANCED, "status": TraceJobStatus.PENDING, "records": 800, "days_ago": 0},
            {"name": "Atlanta Real Estate List", "type": TraceType.NORMAL, "status": TraceJobStatus.FAILED, "records": 300, "days_ago": 2},
        ]
        
        for job_info in jobs_to_create:
            created_at = datetime.utcnow() - timedelta(days=job_info["days_ago"])
            credits_used = job_info["records"] * (3 if job_info["type"] == TraceType.ENHANCED else 1)
            
            job = TraceJob(
                user_id=user_id,
                name=job_info["name"],
                type=job_info["type"],
                status=job_info["status"],
                total_records=job_info["records"],
                processed_records=job_info["records"] if job_info["status"] == TraceJobStatus.COMPLETED else (job_info["records"] // 2 if job_info["status"] == TraceJobStatus.PROCESSING else 0),
                successful_records=int(job_info["records"] * 0.9) if job_info["status"] == TraceJobStatus.COMPLETED else 0,
                credits_used=credits_used if job_info["status"] != TraceJobStatus.PENDING else 0,
                created_at=created_at,
                updated_at=created_at + timedelta(hours=1),
                completed_at=created_at + timedelta(hours=2) if job_info["status"] == TraceJobStatus.COMPLETED else None
            )
            db.add(job)
            db.flush()
            
            # Add some results for completed jobs
            if job_info["status"] == TraceJobStatus.COMPLETED:
                for i in range(3):
                    result = TraceResult(
                        trace_job_id=job.id,
                        input_record=json.dumps({"address": f"{100+i} Main St", "city": "Austin", "state": "TX", "zip": "78701"}),
                        output_record=json.dumps({"owner_name": f"Test Owner {i}", "phone_numbers": ["555-0101", "555-0102"]}),
                        status="success",
                        credits_used=3 if job.type == TraceType.ENHANCED else 1,
                        created_at=job.completed_at
                    )
                    db.add(result)

        # 4. Seed Manual Searches
        print("Adding manual searches...")
        searches = [
            {"query": "123 Maple St, Dallas TX", "type": ManualSearchType.PROPERTY},
            {"query": "John Doe, Miami FL", "type": ManualSearchType.OWNER},
            {"query": "555-0199", "type": ManualSearchType.PHONE},
        ]
        
        for s_info in searches:
            search = ManualSearch(
                user_id=user_id,
                search_type=s_info["type"],
                search_query=s_info["query"],
                credits_used=1,
                status="completed",
                results=json.dumps({"found": True, "details": "Representative search result"}),
                created_at=datetime.utcnow() - timedelta(hours=5)
            )
            db.add(search)

        # 5. Seed DNC Scrub Jobs
        print("Adding DNC scrub jobs...")
        dnc_jobs = [
            {"name": "Marketing Campaign #1", "status": DncScrubStatus.COMPLETED, "records": 5000},
            {"name": "Cold Call List July", "status": DncScrubStatus.PROCESSING, "records": 2500},
        ]
        
        for dnc_info in dnc_jobs:
            dnc_job = DncScrubJob(
                user_id=user_id,
                name=dnc_info["name"],
                status=dnc_info["status"],
                total_records=dnc_info["records"],
                clean_records=int(dnc_info["records"] * 0.8) if dnc_info["status"] == DncScrubStatus.COMPLETED else 0,
                dnc_records=int(dnc_info["records"] * 0.2) if dnc_info["status"] == DncScrubStatus.COMPLETED else 0,
                credits_used=dnc_info["records"] // 10,  # Example rate
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.add(dnc_job)

        db.commit()
        print("[SUCCESS] Dashboard test data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding failed: {type(e).__name__}: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
