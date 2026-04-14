import sys
import os

# Set up paths to import the app
sys.path.append(os.path.join(os.getcwd(), 'tracify_backend', 'backend'))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.api_key import APIKey
from app.models.credit import CreditBalance, CreditTransaction, CreditTransactionType, CreditPackage
from app.models.trace import TraceJob, ManualSearch, TraceResult, PropertyRecord
from app.models.dnc import DncScrubJob, DncScrubResult, DncRecord
from datetime import datetime

def add_credits():
    email = "raohamzanisar43@gmail.com"
    amount = 5000
    
    print(f"Adding {amount} credits to {email}...")
    
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"[ERROR] User {email} not found!")
            return
            
        # Check for existing balance
        balance = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first()
        if not balance:
            balance = CreditBalance(
                user_id=user.id,
                current_credits=0,
                total_purchased=0,
                total_used=0,
                total_bonus=0,
                effective_rate=0.02
            )
            db.add(balance)
            db.flush()
            
        # Update balance
        balance.current_credits += amount
        balance.total_bonus += amount
        balance.last_updated = datetime.utcnow()
        
        # Log transaction
        transaction = CreditTransaction(
            user_id=user.id,
            transaction_type=CreditTransactionType.BONUS,
            amount=amount,
            balance_after=balance.current_credits,
            description="Welcome bonus credits",
            created_at=datetime.utcnow()
        )
        db.add(transaction)
        
        db.commit()
        print(f"[SUCCESS] Added {amount} credits!")
        print(f"          New balance: {balance.current_credits}")
        db.close()
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    add_credits()
