"""
Seed credit packages for Tracerfy Backend
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tracify_backend', 'backend'))

from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.credit import CreditPackage
from decimal import Decimal

def seed_credit_packages():
    """Seed default credit packages"""
    
    packages = [
        {
            "name": "Starter Pack",
            "credits": 1000,
            "price": Decimal("20.00"),
            "description": "Perfect for getting started with our tracing services",
            "bonus_credits": 0,
            "is_active": True
        },
        {
            "name": "Professional Pack", 
            "credits": 2000,
            "price": Decimal("40.00"),
            "description": "Great for regular users and small businesses",
            "bonus_credits": 0,
            "is_active": True
        },
        {
            "name": "Business Pack",
            "credits": 5000,
            "price": Decimal("100.00"),
            "description": "Ideal for growing businesses with moderate usage",
            "bonus_credits": 500,
            "is_active": True
        },
        {
            "name": "Enterprise Pack",
            "credits": 10000,
            "price": Decimal("200.00"),
            "description": "Perfect for large teams and high-volume usage",
            "bonus_credits": 1000,
            "is_active": True
        },
        {
            "name": "Ultimate Pack",
            "credits": 20000,
            "price": Decimal("400.00"),
            "description": "Maximum value for enterprise-level operations",
            "bonus_credits": 2500,
            "is_active": True
        }
    ]
    
    # Create database session
    from app.db.session import SessionLocal
    db = SessionLocal()
    
    try:
        # Clear existing packages
        db.query(CreditPackage).delete()
        
        # Add new packages
        for package_data in packages:
            package = CreditPackage(**package_data)
            db.add(package)
        
        db.commit()
        print("✅ Successfully seeded credit packages:")
        
        for package in db.query(CreditPackage).order_by(CreditPackage.price).all():
            bonus_text = f" + {package.bonus_credits} bonus" if package.bonus_credits > 0 else ""
            print(f"  • {package.name}: {package.credits} credits${bonus_text} - ${package.price}")
        
    except Exception as e:
        print(f"❌ Error seeding credit packages: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_credit_packages()
